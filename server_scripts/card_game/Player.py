import random

from server_scripts.card_game.Cards import *
from server_scripts.card_game import CardExecutor

class Player:
    __slots__ = ('game',
                 'socketId',
                 'deck',
                 'activeGoals',
                 'goals',
                 'hand',
                 'discard',
                 'play',
                 'response',
                 'collections',
                 'tempPlay',
                 'attackers',
                 'breath',
                 'health',
                 'firstTurn')
    def __init__(self, game, socketId):
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
        self.response = []
        self.collections = {
                            'deck':self.deck,
                            'goals':self.goals,
                            'activeGoals':self.activeGoals,
                            'hand':self.hand,
                            'discard':self.discard,
                            'play':self.play,
                            'response':self.response,
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
                await card.reset_rp()
                self.collections[collectionName].append(card)
        elif collectionName == 'activeGoals':
            for cardIndex in range(len(cards)):
                card = await make_goal_card(self, cards.pop(0))
                self.collections[collectionName].append(card)
        elif collectionName == 'response':
            for cardIndex in range(len(cards)):
                card = await make_response_card(self, cards.pop(0))
                self.collections[collectionName].append(card)
        else:
            for c in range(len(cards)):
                card = NotPlayCard(self, cards.pop(0))
                self.collections[collectionName].append(card)
        if collectionName == 'deck' or \
           collectionName == 'goals':
            random.shuffle(collections[collectionName])
        print('collection len is now:',
              len(self.collections[collectionName]))
            




    # sort/access card collections
    async def filter_cards(self, func, collection):
        if not self.game.active:
            return
        return list(filter(lambda x: x[1] is not None and func(x),
                           enumerate(collection)))

    async def get_existing_cards(self, collection):
        return await self.filter_cards(lambda x: True, collection)

    async def get_play_cards(self, func):
        if not self.game.active:
            return
        return await self.filter_cards(func, self.play)

    async def get_unattacked_play_cards(self):
        if not self.game.active:
            return
        return await self.get_play_cards(
            lambda x: not x[1].hasAttacked)
    
    async def get_unactivated_play_cards(self):
        if not self.game.active:
            return
        return await self.get_play_cards(
            lambda x: not x[1].hasActivated)

    async def get_undefended_play_cards(self):
        if not self.game.active:
            return
        return await self.get_play_cards(
            lambda x: not x[1].hasDefended)

    async def get_usable_hand(self):
        if not self.game.active:
            return
        return await self.filter_cards(lambda x: True, self.hand)
    


    
    async def defend_with_card(self, i, opponent):
        if not self.game.active:
            return
        if i >= len(self.play) or self.play[i] is None or \
           self.play[i].hasDefended or len(self.attackers) == 0:
            return False
            
        c = self.play[i]
        a = self.attackers.pop(0)
        print(c.data['name'], 'vs', a.data['name'])
        
        #diff = abs(c.rp-a.rp)
        cdmg = a.rp
        admg = c.rp

        # check response card for destruction
        if await self.check_response_cards(0, opponent, (c,a), c.data['name']):
            # successful, but canceled by response card
            return True
        
        print(c.data['name'], 'takes',cdmg)
        print(a.data['name'], 'takes',admg)
        await c.update_rp(-cdmg)
        await a.update_rp(-admg)

        if c.rp <= 0:
            print(c.data['name'], 'was destroyed')
            await a.add_kill(c)
            await CardExecutor.execute_card_action(a,
                                                   'cardActionOnKill',
                                                      opponent,
                                                      self)
            await self.add_cards_to('discard',[c])
            self.play[i] = None

        if a.rp <= 0:
            print(a.data['name'], 'was destroyed')
            await c.add_defense(a)
            await opponent.add_cards_to('discard',[a])
            print(len(opponent.play))
            if a not in opponent.play:
                print('uhhhh, something weird happened. the attacker isn\'t on the field...?')
            else:
                opponent.play[opponent.play.index(a)] = None

        c.hasDefended = True
        return True

    async def take_card(self, opponent):
        if not self.game.active:
            return
        if len(self.attackers) > 0:
            a = self.attackers.pop(0)
            print('took',a.rp,'from',a.data['name'])
            
            # check response card for direct damage
            if await self.check_response_cards(2,
                                                   opponent,
                                                   a, a.data['name']):
                    # successful, but canceled by response card
                    return True
            
            await a.add_attack()
            await self.update_health(-a.rp)
            return True
        return False

    async def activate_card(self, i, opponent):
        if not self.game.active:
            return
        if i < len(self.play):
            c = self.play[i]

            # get opponent, activate their response card
            for o in self.game.players:
                if o == self: continue
                if await opponent.check_response_cards(3, self, c, c.data['name']):
                    # successful, just got cancled by response card
                    return True
                    
            await CardExecutor.execute_card_action(c, 'cardAction',
                                                   self, opponent)
            c.hasActivated = True
            return True
        return False

    async def attack_with_card(self, i, opponent):
        if not self.game.active:
            return
        if i < len(self.play):
            c = self.play[i]
            opponent.attackers.append(c)
            await CardExecutor.execute_card_action(c, 'cardActionOnAttack',
                                                      self,
                                                      opponent)
            c.hasAttacked = True
            return True
        return False

    async def check_goal_cards(self, phase, opponent):
        return any([await c.check(phase, opponent) \
                    for c in filter(lambda x: x is not None,
                                    self.activeGoals)])

    async def check_response_cards(self, phase, opponent, args=[], msg = ''):

        phaseMessage = ('%s attacked!' % msg,
                        '%s special played!' % msg,
                        'Taking direct damage from %s!' % msg,
                        '%s activated!' % msg,
                        'Attack declared!')[phase]

        msg = phaseMessage + ' Choose response card.'
        
        print('args:',args)
        cards = [ c for c in self.response \
                  if ((c is not None) and \
                   await c.check(phase, opponent, args))]
        if len(cards)>0:
            choices = \
                await self.game.cardGamePlayer.get_cards(self.socketId,
                                    msg,
                                    {'cards':[c.data['name'] for c in cards]}
                                                            )
            print('in check_response_cards',choices)
            out = False
            for _,i in choices:
                print(cards[i].data['name'])
                out = out or await cards[i].run(phase, opponent, args)
            return out
        return False

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
        for c in self.response:
            await c.reset_all()
        await self.remove_none()





    # all functions called by cards must be async.
    # TODO: reexamine deal_cards function, and decide if it's nececelery
    async def deal_cards(self, count):
        if not self.game.active:
            return
        await self.remove_none()
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
        await c.reset_rp()
        rp = c.rp
        if self.breath < rp or \
           (sacrificePoints > 0 and sacrificePoints < rp):
            return False
        
        await self.update_breath(-rp)

        self.hand[i] = None

        if 'action' in c.data['cardType']:
            # it's an action card
            await CardExecutor.execute_card_action(c, 'cardAction',
                                                   self, opponent)
            await self.add_cards_to('discard',[c])

            del c
            return True

        elif 'unit' in c.data['cardType']:
            # onPlay stuff
            await self.add_cards_to('play',[c])
            await CardExecutor.execute_card_action(self.play[-1],
                                                   'cardActionOnPlay',
                                                      self,
                                                      opponent)
            
            return True
        elif 'response' in c.data['cardType']:
            await self.add_cards_to('response',[c])
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

    async def decide(self):
        choices = ['yes','no']
        out = '-1'
        while out not in choices:
            choice = (await self.game.cardGamePlayer.get_text(self.socketId,
                                                'Yes or No?',
                                                {'msgs':choices})
                      )['order'][0][1]
            out = choices[choice]
        return out == 'yes'

    async def checkBreath(self, amount):
        return self.breath < amount


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

        if outCollection == 'play':
            for card in moveCards:
                # check response cards, phase 1 = special play
                # get opponent
                for o in self.game.players:
                    if o == self: continue
                    print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    if await o.check_response_cards(1,
                                                    self,
                                                    card,
                                                    card.data['name']):
                        # it canceled the effect!
                        return

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
            await c.reset_rp()
        
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

    async def set_defend_cooldown(self, amount, tag):
        if not self.game.active:
            return
        cards = await self.get_cards_with_tag('play', tag)
        for c in cards:
            await c.defend_cooldown(amount)
        





        
