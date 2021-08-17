import random
import asyncio

from server_scripts import CardExecutor
from server_scripts.card_game.Game import Game


# TODO: change to CardgameManager
class CardGamePlayer:
    # TODO: write description (with blockquotes)

    __slots__ = ('sio', 'cardManager',
                 'authTokens',
                 'getCardsRes',
                 'games','players',)

    def __init__(self, sio, cardManager):

        self.sio = sio
        self.cardManager = cardManager
        self.authTokens = {}
        self.getCardsRes = {}
        # TODO: remove rooms, if they end up being unnececelery
        self.games = [Game(cardManager, self, i) for i in range(10)]
        self.players = {}


    # socket stuff
    async def client_req_deck(self,sid,data):
        if sid in self.players or \
           data['name'] not in self.cardManager.decks:
            return
        
        await self.add_player(sid, data['name'])

    
    async def res_get_cards(self, sid, data):
        if sid in self.players and \
           sid in self.authTokens and \
           sid in self.getCardsRes and \
           'authToken' in data and \
           data['authToken'] == self.authTokens[sid]:
            del data['authToken']
            self.getCardsRes[sid] = data


    




    async def begin_game(self, game):
        await self.sio.emit('beginGame', {}, room=game.room)

    async def end_game(self, game, msg):
        await self.sio.emit('endGame', {'msg':msg}, room=game.room)

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
            await self.sio.emit('updateCollection', {'operation': operation,
                                                     'collection':collection,
                                                     'yours':p.socketId == sid,
                                                     'cards':tmpCards},
                                room=p.socketId)


    async def update_counters(self, game, sid, counter, amount):
        for p in game.players:
            await self.sio.emit('updateCounters', {  'counter':counter,
                                                     'yours':p.socketId == sid,
                                                     'amount':amount},
                                room=p.socketId)


    async def disp_cards(self, sid, cards, msg):
        if sid not in self.players:
            return
        for p in self.players[sid].players:
            if p.socketId == sid:
                await self.sio.emit('dispCards',
                                    {'msg':'(you) '+msg, 'cards':cards},
                                    room=p.socketId)
            else:
                await self.sio.emit('dispCards',
                                    {'msg':msg, 'cards':cards},
                                    room=p.socketId)
        
    

    async def add_player(self, sid, deck):
        for g in self.games:
            if not g.active:
                self.players[sid] = g
                self.sio.enter_room(sid, g.room)
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
            await self.sio.emit('serverReqChooseCards', cardgroups, room=sid)

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
        self.getCardsRes[sid] = '-1'
        while sid in self.getCardsRes and \
              self.getCardsRes[sid] == '-1':
            # remake authTokn, and send message
            self.authTokens[sid] = random.random()
            textOptions['authToken'] = self.authTokens[sid]
            # used to be playerGetText
            await self.sio.emit('serverReqChooseText', textOptions, room=sid)

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









