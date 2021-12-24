import random

from server_scripts.card_game.Player import Player


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
        self.players = [Player(self,
                               id1,),
                        Player(self,
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
            undefendedPlay = await p.get_undefended_play_cards()
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

            # reveal cards to other player
            await self.cardGamePlayer.disp_cards(
                p.socketId,
                [collectionMap[a][b] for a,b in cardOrder],
                'defend'
                )
    
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
            collectionMapCardType = {
                         'hand':[b.data['cardType'] for a,b in usableHand],
                         'play':[b.data['cardType'] for a,b in unactivatedPlay],
                             }
            collectionMap = {'hand':[b.data['name'] for a,b in usableHand],
                             'play':[b.data['name'] for a,b in unactivatedPlay],
                                 }
            msg = 'Choose the order you want to play or activate cards'
            cardOrder = await self.cardGamePlayer.get_cards(
                            p.socketId, msg, collectionMap)
            print('\n\nNow playing in the following order:',cardOrder)
            self.updateCardOrder = False


            # reveal cards to other player
            await self.cardGamePlayer.disp_cards(
                p.socketId,
                [('cardBack' if 'response' in collectionMapCardType[a][b] else \
                  collectionMap[a][b]) for a,b in cardOrder],
                'play'
                )


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


            # reveal cards to other player
            await self.cardGamePlayer.disp_cards(
                p.socketId,
                [collectionMap[a][b] for a,b in cardOrder],
                'attack'
                )

            
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
