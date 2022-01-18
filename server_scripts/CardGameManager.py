import random
# TODO: I only use asyncio.sleep() from here.
# replace with "from asyncio import sleep"?
import asyncio
from socketio import AsyncServer
from server_scripts.Manager import Manager
from server_scripts.CardManager import CardManager
from server_scripts.card_game.Game import Game


# TODO: change to CardgameManager
class CardGamePlayer(Manager):
    # TODO: write description (with blockquotes)
    # TODO: segregate this class--it should contain ONLY client communication
    #       stuff. Minimal internal processing.

    __slots__ = (
                 'cardManager',
                 'authTokens',
                 'getCardsRes',
                 'games',
                 'players',
                 )

    def __init__(self,
                 namespace: str,
                 datadir : str,
                 cardManager : CardManager 
                 ):
        """
        Initialize class
        TODO: fix later
        """
        super().__init__(namespace, datadir)

        self.cardManager = cardManager
        self.authTokens = {}
        self.getCardsRes = {}
        # TODO: remove rooms, if they end up being unnececelery
        self.games = [Game(cardManager, self, i) for i in range(10)]
        self.players = {}


    ### handle client requests
    async def on_reqQueueGame(self,sid,data):
        if sid in self.players or \
           data['name'] not in self.cardManager.decks:
            return
        
        await self.add_player(sid, data['name'])

    
    async def on_clientResChooseCards(self, sid, data):
        if sid in self.players and \
           sid in self.authTokens and \
           sid in self.getCardsRes and \
           'authToken' in data and \
           data['authToken'] == self.authTokens[sid]:
            del data['authToken']
            self.getCardsRes[sid] = data


    





    ### internal logic
    async def begin_game(self, game):
        await self.emit('beginGame', {}, room=game.room)

    async def end_game(self, game, msg):
        await self.emit('endGame', {'msg':msg}, room=game.room)

    async def update_collection(self, game, sid, collection, operation, cards):
        # TODO: let players know how many cards in goal
        print('in update_collection, len(cards) is:',len(cards))
        for p in game.players:
            # TODO: prbly a better place to do the following check:
            tmpCards = cards
            if (collection in ('hand','activeGoals') and \
               p.socketId != sid and operation=='add') or \
               (collection in ('response') and \
               p.socketId != sid and operation=='add'):
                print('submiting blank data to',p.socketId,
                      'comparing to',sid)
                tmpCards = ["cardBack" for i in cards]
            await self.emit('updateCollection', {'operation': operation,
                                                     'collection':collection,
                                                     'yours':p.socketId == sid,
                                                     'cards':tmpCards},
                                room=p.socketId)


    async def update_counters(self, game, sid, counter, amount):
        for p in game.players:
            await self.emit('updateCounters', {  'counter':counter,
                                                     'yours':p.socketId == sid,
                                                     'amount':amount},
                                room=p.socketId)


    async def disp_cards(self, sid, cards, msg):
        if sid not in self.players:
            return
        for p in self.players[sid].players:
            if p.socketId == sid:
                await self.emit('dispCards',
                                    {'msg':'(you) '+msg, 'cards':cards},
                                    room=p.socketId)
            else:
                await self.emit('dispCards',
                                    {'msg':msg, 'cards':cards},
                                    room=p.socketId)
        
    

    async def add_player(self, sid, deck):
        for g in self.games:
            if not g.active:
                self.players[sid] = g
                self.enter_room(sid, g.room)
                await g.add_player(sid, deck)
                break



    async def remove_player(self, sid):
        g = await self.remove_player_data(sid)
        if g is not None:
            await self.end_game(g, 'A player has disconnected.')

    async def remove_player_data(self, sid):
        if sid not in self.players:
            return None 
        g = self.players[sid]
        del self.players[sid]
        await g.remove_player(sid)
        if sid in self.authTokens:
            del self.authTokens[sid]
        if sid in self.getCardsRes:
            del self.getCardsRes[sid]
        return g




    async def get_cards(self, sid, msg, cardgroups):

        if sid not in self.players:
            return []

        print(msg)

        # set authToken, to prevent cheating
        self.authTokens[sid] = random.random()
        cardgroups['authToken'] = self.authTokens[sid]

        # set misc message properties
        cardgroups['msgId'] = random.random()
        cardgroups['msg'] = msg

        print('sent socket.io msg to',sid, cardgroups)


        # loop until we have a result, remaking authToken every once in a while
        self.getCardsRes[sid] = '-1'
        while sid in self.getCardsRes and \
              self.getCardsRes[sid] == '-1':
            # remake authTokn, and send message
            self.authTokens[sid] = random.random()
            cardgroups['authToken'] = self.authTokens[sid]
            # used to be playerGetCards
            await self.emit('serverReqChooseCards', cardgroups, room=sid)

            # check 10 times for response, before refreshing authToken again.
            for i in range(10):
                await asyncio.sleep(1)
                if sid not in self.players:
                    return []
                if sid not in self.getCardsRes or \
                   self.getCardsRes[sid] != '-1':
                    break
            
        del cardgroups['authToken']
        del cardgroups['msg']
        del cardgroups['msgId']
        
        out = self.getCardsRes[sid]['order']
        del self.getCardsRes[sid]
        print(out)
        return out

    async def get_text(self, sid, msg, textOptions):

        if sid not in self.players:
            return []

        print(msg)

        # set authToken, to prevent cheating
        self.authTokens[sid] = random.random()
        textOptions['authToken'] = self.authTokens[sid]

        # set misc message properties
        textOptions['msgId'] = random.random()
        textOptions['msg'] = msg

        print('sent socket.io msg to',sid, textOptions)


        # loop until we have a result, remaking authToken every once in a while
        # TODO: reduce repeated code between get_choice and get_text
        # ^ in order to do this, maybe make a generic method which takes a
        #   'verification' function as input to make sure the chosen options
        #   are valid?
        self.getCardsRes[sid] = '-1'
        while sid in self.getCardsRes and \
              self.getCardsRes[sid] == '-1':
            # remake authTokn, and send message
            self.authTokens[sid] = random.random()
            textOptions['authToken'] = self.authTokens[sid]
            # used to be playerGetText
            await self.emit('serverReqChooseText', textOptions, room=sid)

            # check 10 times for response, before refreshing authToken again.
            for i in range(10):
                await asyncio.sleep(1)
                if sid not in self.players:
                    return []
                if sid not in self.getCardsRes or \
                   self.getCardsRes[sid] != '-1':
                    break
            
        del textOptions['authToken']
        del textOptions['msg']
        del textOptions['msgId']
        
        out = self.getCardsRes[sid]
        del self.getCardsRes[sid]
        print(out)
        return out









