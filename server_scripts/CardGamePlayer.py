import random
import asyncio
from server_scripts import CardExecutor
from server_scripts.Cards import *




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
            if collection in ('hand','activeGoals') and \
               p.socketId != sid and operation=='add':
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
        await self.sio.emit('dispCards',
                            {'msg':msg, 'cards':cards},
                            room=sid)
        
    

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
            await self.sio.emit('playerGetCards', cardgroups, room=sid)

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
        print('in add_player')
        self.waitingPlayers[sid] = deck

        if len(self.waitingPlayers) == 2:
            id1,id2 = self.waitingPlayers.keys()
            deck1 = self.waitingPlayers[id1]
            deck2 = self.waitingPlayers[id2]
            await self.start_new(id1, id2, deck1, deck2)

            # actually start game?
            await self.run_until_finished()

    async def remove_player(self, sid):
        self.active = False
        if sid in self.waitingPlayers:
            del self.waitingPlayers[sid]
        
    async def start_new(self, id1, id2, deck1, deck2):
        self.active = True
        assert deck1 in self.cardManager.decks
        assert deck2 in self.cardManager.decks
        self.players = [Player(self.cardManager,
                               self,
                               id1,),
                        Player(self.cardManager,
                               self,
                               id2,)]

        # deal
        await self.players[0].first_deal(self.cardManager.decks[deck1])
        await self.players[1].first_deal(self.cardManager.decks[deck2])


        await self.cardGamePlayer.begin_game(self)


        self.turn = random.randint(0,len(self.players)-1)


    async def check_goal_cards(self, phase):
        for pindex in range(len(self.players)):
            p = self.players[pindex]
            o = self.players[(pindex+1)%2]
            if await p.check_goal_cards(phase, o):
                self.active = False
                await self.cardGamePlayer.end_game(self,
                                            'Goal Card Satisfied! Game Over!')
                return


    async def switch_turn(self):
        if not self.active:
            return
        self.turn = (self.turn + 1) % 2




    async def defense_phase(self):
        if not self.active:
            return
        self.inDefensePhase = True
        
        print('\n\ndefense phase for player', self.turn,'\n')

        # shortcut
        p = self.players[self.turn]
        o = self.players[(self.turn+1)%2]


        # update goal cards
        await self.check_goal_cards(0)
        

        
        
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
            collectionMap = {'attackers':[c.data['name'] \
                                          for c in attackers[::-1]],
                             'play':[b.data['name'] \
                                     for a,b in undefendedPlay],
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


        # update goal cards
        await self.check_goal_cards(1)

        
        self.inDefensePhase = False




    async def play_phase(self):
        if not self.active:
            return
        self.inPlayPhase = True


        
        # update goal cards
        await self.check_goal_cards(2)

        
        
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
            collectionMap = {'hand':[b.data['name'] for a,b in usableHand],
                             'play':[b.data['name'] for a,b in unactivatedPlay],
                                 }
            msg = 'Choose the order you want to play or activate cards'
            cardOrder = await self.cardGamePlayer.get_cards(
                            p.socketId, msg, collectionMap)
            print('\n\nNow playing in the following order:',cardOrder)


            # reveal cards to other player
            await self.cardGamePlayer.disp_cards(
                o.socketId,
                [collectionMap[a][b] for a,b in cardOrder],
                'played'
                )

            

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


        
        # TODO: put this in it's own function
        for p in self.players:
            if len(p.deck) == 0:
                # mill!
                self.active = False                
                await self.cardGamePlayer.end_game(self,
                                    'Out of cards in deck! Game Over!')
                return

                
        
        # update goal cards
        await self.check_goal_cards(3)
        
        self.inPlayPhase = False




    async def attack_phase(self):
        if not self.active:
            return
        self.inAttackPhase = True



        
        # update goal cards
        await self.check_goal_cards(4)
        

        
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



        
        # update goal cards
        await self.check_goal_cards(5)

        

        self.inAttackPhase = False
            







    async def run_turn(self):
        if not self.active:
            return
        print('\n\n\nstarting player', self.turn,'turn.\n')
        await self.players[self.turn].update_breath(2)
        await self.players[self.turn].deal_cards(1)
        print('health:', self.players[self.turn].health,
              ' breath:', self.players[self.turn].breath)
        await self.defense_phase()
        await self.play_phase()
        await self.attack_phase()
        if len(self.players)>self.turn:
            await self.players[self.turn].end_turn()
        await self.switch_turn()


    async def run_until_finished(self):
##        try:
        while self.active:
            await self.run_turn()
##        except:
##            print('there was an error :(')
        
        while len(self.players) > 0:
            p = self.players[0]
            await self.cardGamePlayer.remove_player_data(p.socketId)
            if p in self.players:
                await self.remove_player(p)
            self.players.pop(0)






class Player:
    __slots__ = ('cardManager', 'game', 'socketId',
                 'deck',
                 'activeGoals', 'goals',
                 'hand',
                 'discard',
                 'play',
                 'collections',
                 'tempPlay',
                 'attackers',
                 'breath',
                 'health',
                 'firstTurn')
    def __init__(self, cardManager, game, socketId):
        self.cardManager = cardManager
        self.game = game
        self.socketId = socketId
        
        self.tempPlay = [] # for resolving action cards
        self.attackers = [] # to hold incoming attacks

        self.breath = 3
        self.health = 40

        self.firstTurn = True

     

    async def first_deal(self, deck):
        if not self.game.active:
            return
        self.deck = [Card(self) for i in deck['deck']]
        for i in range(len(self.deck)):
            await self.deck[i].load_data(deck['deck'][i])
        random.shuffle(self.deck)
        
        self.goals = [Card(self) for i in deck['goals']]
        for i in range(len(self.goals)):
            await self.goals[i].load_data(deck['goals'][i])
        random.shuffle(self.goals)

        self.activeGoals = []
        
        self.hand = []
        self.discard = []
        self.play = []
        self.collections = {
                            'deck':self.deck,
                            'goals':self.goals,
                            'activeGoals':self.activeGoals,
                            'hand':self.hand,
                            'discard':self.discard,
                            'play':self.play
                            }
        
        await self.deal_cards(6)
        await self.deal_goal_cards(1)





    async def update_health(self, amount):
        if not self.game.active:
            return
        self.health += amount
        await self.game.cardGamePlayer.update_counters(self.game,
                                                     self.socketId,
                                                     'health',
                                                     self.health)
        print('health is now:',self.health)
        if self.health <= 0:
            # lost! game over
            self.game.active = False
            await self.game.cardGamePlayer.end_game(self.game,
                                              'Health is 0! Game Over!')

    async def update_breath(self,amount):
        if not self.game.active:
            return
        self.breath += amount
        await self.game.cardGamePlayer.update_counters(self.game,
                                                       self.socketId,
                                                       'breath',
                                                       self.breath)
        print('breath is now:',self.breath)


    
    # this only exists because of weird card stuff
           
    async def remove_cards_from(self, collectionName, cards):
        if not self.game.active:
            return
        """ removes every index in cards from the specified collection """
        if collectionName in self.collections:
            await self.game.cardGamePlayer.update_collection(self.game,
                                                    self.socketId,
                                                    collectionName,
                                                    'remove',
                                                    cards)
        out =[self.collections[collectionName].pop(i) \
                for i in cards]
        return out

    async def pull_cards_from(self, collectionName, count):
        if not self.game.active:
            return
        """ removes the top <count> cards from the specified collection. """
        print('in pull_cards_from')
        collection = self.collections[collectionName]
        count = min(count, len(collection))
        print('count:',count,
              'len(collection):',len(collection),
              'cards:',[len(collection)-i-1 for i in range(count)])
        return await self.remove_cards_from(
                                     collectionName,
                                     [len(collection)-i-1 \
                                      for i in range(count)],)

    async def add_cards_to(self, collectionName, cards):
        if not self.game.active:
            return
        print('in add_cards_to, collectionName:',collectionName,
              'cards:',cards)
        await self.game.cardGamePlayer.update_collection(self.game,
                                                    self.socketId,
                                                    collectionName,
                                                    'add',
                                        [c.data['name'] for c in cards])

        
        if collectionName == 'hand' and \
           self.game.inPlayPhase and \
           self.game.players[self.game.turn] is self:
            self.game.updateCardOrder = True
            


        
        print('in add_cards_to', cards,
              'current collection len is',
              len(self.collections[collectionName]))
        
        if collectionName == 'play':            
            for cardIndex in range(len(cards)):
                card = PlayCard(self, cards.pop(0))
                self.collections[collectionName].append(card)
        elif collectionName == 'activeGoals':
            for cardIndex in range(len(cards)):
                card = await make_goal_card(self, cards.pop(0))
                self.collections[collectionName].append(card)
        else:
            for c in range(len(cards)):
                newc = NotPlayCard(self, cards.pop(0))
                self.collections[collectionName].append(newc)
        if collectionName == 'deck' or \
           collectionName == 'goals':
            random.shuffle(collections[collectionName])
        print('collection len is now:',
              len(self.collections[collectionName]))
            




    # sort/access card collections
    async def filter_cards(self, func, collection):
        if not self.game.active:
            return
        return list(filter(func, enumerate(collection)))

    async def get_play_cards(self, func):
        if not self.game.active:
            return
        return await self.filter_cards(func, self.play)

    async def get_unattacked_play_cards(self):
        if not self.game.active:
            return
        return await self.get_play_cards(
            lambda x: x[1] is not None and not x[1].hasAttacked)
    
    async def get_unactivated_play_cards(self):
        if not self.game.active:
            return
        return await self.get_play_cards(
            lambda x: x[1] is not None and not x[1].hasActivated)

    async def get_undefended_play_cards(self):
        if not self.game.active:
            return
        return await self.get_play_cards(
            lambda x: x[1] is not None and not x[1].hasDefended)

    async def get_usable_hand(self):
        if not self.game.active:
            return
        return await self.filter_cards(lambda x: x[1] is not None, self.hand)
    


    
    async def defend_with_card(self, i, opponent):
        if not self.game.active:
            return
        if i < len(self.play) and self.play[i] is not None and \
           len(self.attackers) > 0:
            c = self.play[i]
            a = self.attackers.pop(0)
            print(c.data['name'], 'vs', a.data['name'])
            
            #diff = abs(c.rp-a.rp)
            cdmg = a.rp
            admg = c.rp
            print(c.data['name'], 'takes',cdmg)
            print(a.data['name'], 'takes',admg)
            await c.update_rp(-cdmg)
            await a.update_rp(-admg)

            if c.rp <= 0:
                print(c.data['name'], 'was destroyed')
                await a.add_kill(c)
                await CardExecutor.execute_card_action_on(a,
                                                          opponent,
                                                          self,
                                                          2)
                await self.add_cards_to('discard',[c])
                self.play[i] = None

            if a.rp <= 0:
                print(a.data['name'], 'was destroyed')
                await c.add_defense(a)
                await opponent.add_cards_to('discard',[a])
                print(len(opponent.play))
                opponent.play[opponent.play.index(a)] = None

            c.hasAttacked = True
            return True
        return False

    async def take_card(self, opponent):
        if not self.game.active:
            return
        if len(self.attackers) > 0:
            a = self.attackers.pop(0)
            print('took',a.rp,'from',a.data['name'])
            await a.add_attack()
            await self.update_health(-a.rp)
            return True
        return False

    async def activate_card(self, i, opponent):
        if not self.game.active:
            return
        if i < len(self.play):
            c = self.play[i]
            await CardExecutor.execute_card_action(c, self, opponent)
            c.hasActivated = True
            return True
        return False

    async def attack_with_card(self, i, opponent):
        if not self.game.active:
            return
        if i < len(self.play):
            c = self.play[i]
            opponent.attackers.append(c)
            await CardExecutor.execute_card_action_on(c,
                                                      self,
                                                      opponent,
                                                      1)
            c.hasAttacked = True
            return True
        return False

    async def check_goal_cards(self, phase, opponent):
        return any([await c.check(phase, opponent) \
                    for c in filter(lambda x: x is not None,
                                    self.activeGoals)])

    async def remove_none(self):
        if not self.game.active:
            return
        for collectionName in self.collections:
            while None in self.collections[collectionName]:
                await self.remove_cards_from(collectionName,
                        (self.collections[collectionName].index(None),))

    async def end_defense_phase(self):
        if not self.game.active:
            return
##        await self.add_cards_to('discard', self.tempPlay)
        await self.remove_none()

    async def end_play_phase(self):
        if not self.game.active:
            return
##        await self.add_cards_to('discard', self.tempPlay)
        await self.remove_none()
            
        if self.firstTurn:
            self.firstTurn = False
            for c in self.play:
                c.hasAttacked = True
        

    async def end_turn(self):
        if not self.game.active:
            return
        for c in self.play:
            await c.reset_all()
        await self.remove_none()





    # all functions called by cards must be async.
    # TODO: reexamine deal_cards function, and decide if it's nececelery
    async def deal_cards(self, count):
        if not self.game.active:
            return
        cards = await self.pull_cards_from('deck', count)
        print('in deal_cards, dealing',len(cards),'cards.')
        await self.add_cards_to('hand', cards)
            
    async def deal_goal_cards(self, count):
        if not self.game.active:
            return
        print(self.goals[0].data)
        cards = await self.pull_cards_from('goals', count)
        print(cards)
        print([c.data for c in cards])
        print([c.data['name'] for c in cards])
        await self.add_cards_to('activeGoals', cards)


    async def normal_play_card(self, i, opponent, sacrificePoints=-1):
        if not self.game.active:
            return
        if i >= len(self.hand) or self.hand[i] is None:
            return False

        
        c = self.hand[i]
        print('\nplaying', c.data['name'])
        


        # breath managment
        # TODO fully implement sacrifice
        rp = int(c.data['cost'])
        if self.breath < rp or \
           (sacrificePoints > 0 and sacrificePoints < rp):
            return False
        
        await self.update_breath(-rp)

        self.hand[i] = None

        if 'action' in c.data['cardType']:
            # it's an action card
            await CardExecutor.execute_card_action(c, self, opponent)
            await self.add_cards_to('discard',[c])

            del c
            return True

        elif 'unit' in c.data['cardType']:
            # onPlay stuff
            await self.add_cards_to('play',[c])
            await CardExecutor.execute_card_action_on(self.play[-1],
                                                      self,
                                                      opponent,
                                                      0)
            
            return True
        elif 'response' in c.data['cardType']:
            return True
        else:
            # shouldn't get here
            print('cardType without unit, action, or response in it! Bad!')
            print(c.data['name'])
            return False
        return False







    # things that get used by things that get used by cards

    async def remove_card_tags(self):
        if not self.game.active:
            return
        for collectionName in self.collections:
            for c in self.collections[collectionName]:
                if c is not None:
                    await c.reset_tags()

    async def get_cards_with_tag(self, collectionName, tag):
        if not self.game.active:
            return
        return list(filter(
                    lambda x: x is not None and tag in x.tags,
                    self.collections[collectionName]
                   ))


    # things that get used by cards

    async def spy_cards_from(self, collectionName, count, tag):
        if not self.game.active:
            return
        """returns the top <count> cards from the specified collection"""
        if count == 0:
            count = len(self.collections[collectionName])
        for c in self.collections[collectionName][::-1][:count]:
            if c is not None:
                print(c.data['name'])
            else:
                print(c)
        for c in list(filter(lambda x: x is not None,
                self.collections[collectionName][::-1]))[:count]:
            print('added tag',tag,'to',c.data['name'])
            await c.add_tag(tag)

    async def search_cards_in(self, collectionName, rarity, unitType, tag):
        if not self.game.active:
            return
        print('in search_cards_in')
        collection = self.collections[collectionName]

        cardTypes = [card.data['cardType'] if card is not None else '' \
                     for card in collection]

        
        print(cardTypes)
        for i in range(len(collection)):
            ctypes = cardTypes[i].split(' ')
            print('ctypes:',ctypes)
            if len(ctypes) >= 3 and \
               'unit' in ctypes and \
               (rarity=='any' or rarity==ctypes[0]) and \
               (unitType=='any' or unitType==ctypes[1]):
                print('added', ctypes)
                await collection[i].add_tag(tag)
        

    async def check_cards_tag(self, collectionName, count, tag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag(collectionName, tag)
        print('in check_cards_tag, len(cards) is:',len(cards))
        return len(cards) >= count
                

    async def disp_cards(self, player, collectionName, tag):
        if not self.game.active:
            return
        cards = await player.get_cards_with_tag(collectionName, tag)
        cardNames = [c.data['name'] for c in cards]
        print('in disp cards', cardNames)
        await self.game.cardGamePlayer.disp_cards(self.socketId,
                                                  cardNames,
                                                  'reveal')
    

    async def choose_cards(self, player, collectionName,
                           limit, intag, outtag):
        if not self.game.active:
            return
        cards = await player.get_cards_with_tag(collectionName, intag)

        print('in choose_cards')
        print('choosing out of:',cards)
        
        limit = min(limit, len(cards))

        if limit > 0:
            out = await self.game.cardGamePlayer.get_cards(self.socketId,
                                               'Choose '+str(limit),
                                    {'cards':[c.data['name'] for c in cards]}
                                                            )
            while len(out) != limit:
                out = await self.game.cardGamePlayer.get_cards(self.socketId,
                                               'Choose '+str(limit),
                                    {'cards':[c.data['name'] for c in cards]}
                                                            )
        else:
            out = []
        print('chosen',[cards[b] for a,b in out])
        for a,b in out:
            await cards[b].add_tag(outtag)

        # shuffle deck after player gets to see it
        if collectionName == 'deck':
            random.shuffle(self.collections[collectionName])

    async def remove_card_tags_with_tag(self, collectionName, intag, outtag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag(collectionName, intag)
        for c in cards:
            if c is not None:
                await c.remove_tag(outtag)
                
            

    async def move_cards(self, inCollection, outCollection, tag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag(inCollection, tag)
        cardIndex = [self.collections[inCollection].index(c) for c in cards]
        cardIndex.sort()
        cardIndex = cardIndex[::-1]
        print('in move_cards, cardIndex is:',cardIndex)

        moveCards = [self.collections[inCollection][i] for i in cardIndex]
        for i in cardIndex:
            self.collections[inCollection][i] = None
        
        await self.add_cards_to(outCollection,moveCards)




    
    async def set_rp(self, amount, tag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag('play', tag)
        for c in cards:
            await c.set_rp(amount)

    async def reset_rp(self, tag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag('play', tag)
        for c in cards:
            await c.reset_rp(amount)
        
    async def increase_rp(self, amount, tag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag('play', tag)
        for c in cards:
            await c.update_rp(amount)
            
    async def set_activate_cooldown(self, amount, tag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag('play', tag)
        for c in cards:
            await c.activate_cooldown(amount)

    async def set_attack_cooldown(self, amount, tag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag('play', tag)
        for c in cards:
            await c.attack_cooldown(amount)
        





        
