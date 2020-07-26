import random
import asyncio
from server_scripts import CardExecutor

class CardGamePlayer:

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


    




    async def begin_game(self, room, pids, data):
        for i in range(len(pids)):
            print('sending beginGame to', pids[i])
            await self.sio.emit('beginGame', data[i], room=pids[i])

    async def add_to_discard(self, game, sid, cards):
        for p in game.players:
            await self.sio.emit('updateCollection', {'add': True,
                                                     'collection':'discard',
                                                     'yours':p.socketId == sid,
                                                     'cards':cards},
                                room=p.socketId)

    async def add_player(self, sid, deck):
        for g in self.games:
            if not g.active:
                self.players[sid] = g
                await g.add_player(sid, deck)
                self.sio.enter_room(sid, g.room)
                break



    async def remove_player(self, sid):
        if sid not in self.players:
            return
        await self.players[sid].remove_player(sid)
        del self.players[sid]
        if sid in self.authTokens:
            del self.authTokens[sid]
        if sid in self.getCardsRes:
            del self.getCardsRes[sid]



        
##        await asyncio.sleep(1)
##        self.authTokens[sid] = random.random()
##        print(self.authTokens[sid])
##        await self.sio.emit(
##            'playerGetCards', {'hand':['Breath User Jaycob'],
##                               'deck':['Call of Hades'],
##                               'authToken':self.authTokens[sid],},
##            room=sid)
##
##    async def chooseCards(self,sid,data):
##        print('in chooseCards',data, data['authToken'], self.authTokens[sid])
##        if not sid in self.authTokens or \
##           data['authToken'] != self.authTokens[sid]:
##            return
##        # TODO: delete the rest of these eventually
##        del self.authTokens[sid]
##        del data['authToken']
##        print(data['order'])




    # TODO: actually make this online
    async def get_cards(self, sid, msg, cardgroups):
        print(msg)




        # TODO: send message more than once
        self.authTokens[sid] = random.random()
        cardgroups['authToken'] = self.authTokens[sid]
        cardgroups['msg'] = msg
        print('sent socket.io msg to',sid, cardgroups)
        await self.sio.emit('playerGetCards', cardgroups, room=sid)
        del cardgroups['authToken']
        del cardgroups['msg']


        
        
        self.getCardsRes[sid] = '-1'

        while self.getCardsRes[sid] == '-1':
            await asyncio.sleep(1)
##        while not all([(o in [(cgn+'-'+str(i)) for cgn in cardgroups \
##                              for i in range(len(cardgroups[cgn]))]) \
##                       for o in out.split()]):
##            #out = input('  > ')
##            pass
        out = self.getCardsRes[sid]['order']
        del self.getCardsRes[sid]
        print(out)
        return out

                      


class Game:
    __slots__ = ('cardManager', 'cardGamePlayer', 'room',
                 'active',
                 'waitingPlayers',
                 'players','turn',
                 'inDefensePhase', 'inPlayPhase', 'inAttackPhase',
                 'updateCardOrder')
    def __init__(self, cardManager, cardGamePlayer, roomnumber):
        self.cardManager = cardManager
        self.cardGamePlayer = cardGamePlayer
        self.room = 'game-room-'+str(roomnumber)

        self.active = False

        self.waitingPlayers = {}
        self.players = []
        self.turn = 0
        
        self.inDefensePhase = False
        self.inPlayPhase = False
        self.inAttackPhase = False

        self.updateCardOrder = False

    async def add_player(self, sid, deck):
        self.waitingPlayers[sid] = deck

        if len(self.waitingPlayers) == 2:
            id1,id2 = self.waitingPlayers.keys()
            deck1 = self.waitingPlayers[id1]
            deck2 = self.waitingPlayers[id2]
            await self.start_new(id1, id2, deck1, deck2)

        # actually start game?
        await self.run_until_finished()

    async def remove_player(self, sid):
        del self.waitingPlayers[sid]
        self.active = False
        
    async def start_new(self, id1, id2, deck1, deck2):
        self.active = True
        assert deck1 in self.cardManager.decks
        assert deck2 in self.cardManager.decks
        self.players = [Player(self.cardManager,
                               self,
                               id1,
                               self.cardManager.decks[deck1]),
                        Player(self.cardManager,
                               self,
                               id2,
                               self.cardManager.decks[deck2])]

        # deal
        for p in self.players:
            await p.first_deal()


        await self.cardGamePlayer.begin_game(self.room,
                [p.socketId for p in self.players],
                [{'hand':p.hand,
                  'activeGoals':p.activeGoals} \
                         for p in self.players]
                                       )


        self.turn = random.randint(0,len(self.players)-1)



    async def switch_turn(self):
        self.turn = (self.turn + 1) % 2




    async def defense_phase(self):
        
        self.inDefensePhase = True
        print('\n\ndefense phase for player', self.turn,'\n')

        # shortcut
        p = self.players[self.turn]
        o = self.players[(self.turn+1)%2]

        
        
        # main loop in case anything causes a redo to be necessary.
        self.updateCardOrder = True
        while self.updateCardOrder:

            # get card Order
            attackers = p.attackers[::-1]
            # reverse the attackers so they're in the order played
            undefendedPlay = await p.get_unattacked_play_cards()
            if len(p.attackers) == 0:
                print('Skipping defense phase, no attackers.')
                return
            collectionMap = {'attackers':[c.data['name'] for c in attackers],
                             'play':[b.data['name'] for a,b in undefendedPlay],
                                 }
            msg = 'Choose the order of cards you want to defend with'
            cardOrder = await self.cardGamePlayer.get_cards(
                            p.socketId, msg, collectionMap)
            print('\n\nNow playing in the following order:',cardOrder)
            self.updateCardOrder = False
    
            # break if all attacks have already resolved
            if len(undefendedPlay) == 0:
                break

            
            # TODO: custom activation unit cards (on play, on attack)
            for collection, i in cardOrder:
                success = True
                if collection == 'play':
                    playIndex = undefendedPlay[i][0]
                    # TODO: make the opponent buisiness in a
                    # separate function for easy editing later
                    success = await p.defend_with_card(playIndex,o)
                elif collection == 'attackers':
                    success = await p.take_card(o)
                    
                else:
                    success = False
                
                if not success or self.updateCardOrder:
                    print('attack attempt failed' if not success else \
                          'update card order\n')
                    break

        while len(p.attackers) > 0:
            await p.take_card(o)

        # TODO: rename this function. It doesn't make sense
        await p.end_defense_phase()
        await o.end_defense_phase()
        
        self.inDefensePhase = False




    async def play_phase(self):
        self.inPlayPhase = True
        
        # TODO: implement sacrifice to play cards
        
        # TODO: how to deal with things which change play in the middle
        # (more breath, new cards, etc.)
        # do certain cards allow you to change the order?
            
        print('\n\n\nplay phase for player', self.turn,'\n')

        # shortcut
        p = self.players[self.turn]
        o = self.players[(self.turn+1)%2]

        

        # main loop in case anything causes a redo to be necessary.
        self.updateCardOrder = True
        while self.updateCardOrder:

            # get card Order
            usableHand = await p.get_usable_hand()
            unactivatedPlay = await p.get_unactivated_play_cards()
            if len(usableHand) == 0 and len(unactivatedPlay)==0:
                print('Skipping play phase, no hand/play cards.')
                return
            collectionMap = {'hand':[b for a,b in usableHand],
                             'play':[b.data['name'] for a,b in unactivatedPlay],
                                 }
            msg = 'Choose the order you want to play or activate cards'
            cardOrder = await self.cardGamePlayer.get_cards(
                            p.socketId, msg, collectionMap)
            print('\n\nNow playing in the following order:',cardOrder)

            self.updateCardOrder = False


            # execute card order
            # TODO: check for response cards
            # TODO: custom activation unit cards (on play, on attack)
            for collection, i in cardOrder:
                success = True
                if collection == 'hand':
                    handIndex = usableHand[i][0]
                    # TODO: make the opponent buisiness in a
                    # separate function for easy editing later
                    success = await p.normal_play_card(handIndex,o)
                elif collection == 'play':
                    # TODO: make the opponent buisiness in a
                    # separate function for easy editing later
                    playIndex = unactivatedPlay[i][0]
                    success = await p.activate_card(playIndex,o)
                    
                else:
                    success = False

                if not success or self.updateCardOrder:
                    print('play attempt failed' if not success else \
                          'update card order\n')
                    break


        await p.end_play_phase()
        
        self.inPlayPhase = False




    async def attack_phase(self):
        self.inAttackPhase = True
        print('\n\n\nattack phase for player', self.turn,'\n')

        # shortcut
        p = self.players[self.turn]
        o = self.players[(self.turn+1)%2]

        
        # main loop in case anything causes a redo to be necessary.
        self.updateCardOrder = True
        while self.updateCardOrder:

            # get card Order
            unattackedPlay = await p.get_unattacked_play_cards()
            if len(unattackedPlay)==0:
                print('Skipping attack phase, no play cards.')
                return
            collectionMap = {'play':[b.data['name'] for a,b in unattackedPlay],
                                 }
            msg = 'Choose the order of cards you want to attack with'
            cardOrder = await self.cardGamePlayer.get_cards(
                            p.socketId, msg, collectionMap)
            print('\n\nNow playing in the following order:',cardOrder)
            self.updateCardOrder = False

            
            # TODO: custom activation unit cards (on play, on attack)
            for collection, i in cardOrder:
                success = True
                if collection == 'play':
                    playIndex = unattackedPlay[i][0]
                    # TODO: make the opponent buisiness in a
                    # separate function for easy editing later
                    success = await p.attack_with_card(playIndex,o)
                    
                else:
                    success = False

                if not success or self.updateCardOrder:
                    print('attack attempt failed' if not success else \
                          'update card order\n')
                    break

        self.inAttackPhase = False
            







    async def run_turn(self):
        print('\n\n\nstarting player', self.turn,'turn.\n')
        await self.players[self.turn].increase_breath(2)
        await self.players[self.turn].deal_cards(1)
        print('health:', self.players[self.turn].health,
              ' breath:', self.players[self.turn].breath)
        await self.defense_phase()
        await self.play_phase()
        await self.attack_phase()
        await self.players[self.turn].end_turn()
        await self.switch_turn()


    async def run_until_finished(self):
        while self.active:
            await self.run_turn()







class Player:
    __slots__ = ('cardManager', 'game', 'socketId',
                 'deck',
                 'activeGoals', 'goals',
                 'hand',
                 'discard',
                 'play',
                 'tempPlay',
                 'attackers',
                 'breath',
                 'health',
                 'firstTurn')
    def __init__(self, cardManager, game, socketId, deck):
        self.cardManager = cardManager
        self.game = game
        self.socketId = socketId

        
        self.deck = deck['deck'].copy()
        random.shuffle(self.deck)
        
        self.goals = deck['goals'].copy()
        random.shuffle(self.deck)

        self.activeGoals = []
        
        self.hand = []
        self.discard = []
        self.play = []
        self.tempPlay = [] # for resolving action cards
        self.attackers = [] # to hold incoming attacks

        self.breath = 3
        self.health = 40

        self.firstTurn = True

     

    async def first_deal(self):
        await self.deal_cards(6)
        await self.deal_goal_cards(1)


    async def pull_cards_from(self, count, collection):
        return [collection.pop() for i in range(min(count,len(collection)))]

    async def discard_cards(self, cards):
        await self.game.cardGamePlayer.add_to_discard(self.game,
                                                      self.socketId,
                                                      cards)
        for c in cards:
            self.discard.append(self.tempPlay.pop(0))

    async def filter_cards(self, func, collection):
        return list(filter(func, enumerate(collection)))

    async def get_play_cards(self, func):
        return await self.filter_cards(func, self.play)

    async def get_unattacked_play_cards(self):
        return await self.get_play_cards(
            lambda x: x[1] is not None and not x[1].hasAttacked)
    
    async def get_unactivated_play_cards(self):
        return await self.get_play_cards(
            lambda x: x[1] is not None and not x[1].hasActivated)

    async def get_undefended_play_cards(self):
        return await self.get_play_cards(
            lambda x: x[1] is not None and not x[1].hasDefended)

    async def get_usable_hand(self):
        return await self.filter_cards(lambda x: x[1] is not None, self.hand)
    


    
    async def defend_with_card(self, i, opponent):
        if i < len(self.play) and self.play[i] is not None and \
           len(self.attackers) > 0:
            c = self.play[i]
            a = self.attackers.pop(0)
            print(c.data['name'], 'vs', a.data['name'])
            
            #diff = abs(c.rp-a.rp)
            cdmg = a.rp
            admg = c.rp
            print(c.data['name'], 'takes',admg)
            print(a.data['name'], 'takes',cdmg)
            c.rp -= admg
            a.rp -= cdmg

            # TODO: move cards to discard when destroyed
            if c.rp <= 0:
                print(c.data['name'], 'was destroyed')
                self.play[i] = None
            if a.rp <= 0:
                print(a.data['name'], 'was destroyed')
                opponent.play[i] = None
            
            c.hasActivated = True
            return True
        return False

    async def take_card(self, opponent):
        if len(self.attackers) > 0:
            a = self.attackers.pop(0)
            self.health -= a.rp
            print('took',a.rp,'from',a.data['name'],
                  ' health is now:',self.health)
            return True
        return False

    async def activate_card(self, i, opponent):
        if i < len(self.play):
            c = self.play[i]
            await CardExecutor.execute_card_action(c, i, self, opponent)
            c.hasActivated = True
            return True
        return False

    async def attack_with_card(self, i, opponent):
        if i < len(self.play):
            c = self.play[i]
            opponent.attackers.append(c)
            c.hasAttacked = True
            return True
        return False
        

    async def play_card(self, c, i, opponent):
        # TODO: improve this system
        # [have unit in name for unit]
        # [have action in the name for action]
        # [have reponse in the name for response]            
        if len(c.data['cardType']) == 0 or c.data['cardType']=='default':
            # it's an action card
            await CardExecutor.execute_card_action(c, i, self, opponent)
            self.tempPlay.append(c.data['name'])
            del c
            return True

        else:
            # it's an action care
            self.play.append(c)
            return True
        return False


    async def end_defense_phase(self):
        while None in self.play:
            self.play.remove(None)

    async def end_play_phase(self):
        await self.discard_cards(self.tempPlay)
        while None in self.hand:
            self.hand.remove(None)
        if self.firstTurn:
            self.firstTurn = False
            for c in self.play:
                c.hasAttacked = True
        

    async def end_turn(self):
        for c in self.play:
            await c.reset_all()





    # all functions called by cards must be async.
    async def increase_breath(self, amount):
        self.breath += amount

    async def deal_cards(self, count):
        cards = await self.pull_cards_from(count, self.deck)
        for c in cards:
            self.hand.append(c)
            print('dealt:',c)
        if self.game.inPlayPhase and \
           self.game.players[self.game.turn] is self:
            self.game.updateCardOrder = True
            
    async def deal_goal_cards(self, count):
        cards = await self.pull_cards_from(count, self.goals)
        for c in cards:
            self.activeGoals.append(c)


    async def normal_play_card(self, i, opponent, sacrificePoints=-1):
        if i < len(self.hand) and self.hand[i] is not None:
            cardName = self.hand[i]
            print('\nplaying', cardName)
            
            c = PlayCard(self.cardManager)
            await c.load_data(cardName)


            # breath managment
            # TODO fully implement sacrifice
            if self.breath < int(c.rp) or \
               (sacrificePoints > 0 and sacrificePoints < int(c.rp)):
                return False
            
            self.breath -= c.rp
            self.hand[i] = None

            return await self.play_card(c, i, opponent)
        return False






        

class PlayCard:
    __slots__ = ('cardManager', 'data', 'rp',
                 'hasDefended', 'hasActivated', 'hasAttacked')
    def __init__(self, cardManager):
        self.cardManager = cardManager
        self.hasDefended = False
        self.hasActivated = True # can't activate on first turn played
        self.hasAttacked = False

    # all functions called by cards must not be async.
    async def increase_rp(self, amount):
        self.rp += amount


    async def reset_all(self):
        self.hasDefended = False
        self.hasActivated = False
        self.hasAttacked = False


    async def load_data(self, cardName):
        
        self.data = await self.cardManager.getCardByName(cardName)
        self.rp = int(self.data['cost'])

    
