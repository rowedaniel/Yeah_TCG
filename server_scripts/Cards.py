
# Base Card class
class Card:
    __slots__ = ('player', 'data', 'tags')

    
    def __init__(self, player):
        self.player = player
        self.tags = []

    async def add_tag(self,tag):
        if not self.player.game.active:
            return
        if tag not in self.tags:
            self.tags.append(tag)

    async def remove_tag(self,tag):
        if not self.player.game.active:
            return
        if tag in self.tags:
            self.tags.remove(tag)

    async def reset_tags(self):
        if not self.player.game.active:
            return
        self.tags = []

        
    async def load_data(self, cardName):
        if not self.player.game.active:
            return
        
        self.data = await self.player.game.cardManager.getCardByName(cardName)






# all normal cards
class NotPlayCard(Card):
    __slots__ = ('rp',
                 )
    def __init__(self, player, card):
        super().__init__(player)
        self.data = card.data
        self.rp = 0

    async def parse_rp(self, coststr):
        try:
            return int(coststr)
        except:
            if coststr == 'X':
                print('in parse_rp')
                if 'parseCost' in self.data:
                    print(self.data['parseCost'])
                    if self.data['parseCost'] == 'any':
                        costs = [str(i) for i in range(0,self.player.breath+1)]
                        out = '-1'
                        while out not in costs:
                            choice = \
                              (await self.player.game.cardGamePlayer.get_text(
                                self.player.socketId,
                                'How much breath do you want to pay?',
                                {'msgs':costs}
                                ))['order'][0][1]
                            print(choice)
                            out = costs[choice]
                            # TODO: this might bomb. Fix later in get_text
                        return int(out)
                    elif 'length' in self.data['parseCost']:
                        if 'discard' in self.data['parseCost']:
                            return len(self.player.discard)
            return 0

    async def reset_rp(self):
        if not self.player.game.active:
            return
        # TODO: make this work with Roid Rage
        self.rp = await self.parse_rp(self.data['cost'])
                






# play cards
class PlayCard(NotPlayCard):
    __slots__ = ('kills', 'attacks', 'defenses',
                 'hasDefended', 'defendCooldown',
                 'hasActivated', 'activateCooldown',
                 'hasAttacked', 'attackCooldown'
                 )
    def __init__(self, player, card):
        super().__init__(player, card)
        # TODO: make this work with Roid Rage

        
        self.hasDefended = False
        self.hasActivated = True # can't activate on first turn played
        self.hasAttacked = False
        self.defendCooldown = 0
        self.activateCooldown = 0
        self.attackCooldown = 0

        # TODO: make it so that these get updated
        self.attacks = []  # attack successfully got through to player
        self.kills = []    # killed another card by attacking
        self.defenses = [] # defended agaisnt another card

    # all functions called by cards must not be async.
    async def set_rp(self, amount):
        if not self.player.game.active:
            return
        self.rp = await self.parse_rp(amount)
        if self in self.player.play: # just in case
            await self.player.game.cardGamePlayer.update_counters(
                self.player.game,
                self.player.socketId,
                'rp',
                [self.player.play.index(self), self.rp]
                )

    async def update_rp(self, amount):
        if not self.player.game.active:
            return
        await self.set_rp(self.rp + await self.parse_rp(amount))

    async def reset_rp(self):
        await self.set_rp(await self.parse_rp(self.data['cost']))

    async def add_attack(self):
        self.attacks.append(self.rp)
        
    async def add_kill(self, other):
        self.kills.append(other.data)

    async def add_defense(self, other):
        self.defenses.append(other.data)                                                                       

    async def activate_cooldown(self, amount):
        if not self.player.game.active:
            return
        print('set activate cooldown for:',amount)
        self.hasActivated = True
        if self.activateCooldown != -1:
            self.activateCooldown = amount
    async def attack_cooldown(self, amount):
        if not self.player.game.active:
            return
        print('set attack cooldown for:',amount)    
        self.hasAttacked = True
        if self.attackCooldown != -1:
            self.attackCooldown = amount     
    async def defend_cooldown(self, amount):
        if not self.player.game.active:
            return
        print('set defend cooldown for:',amount)    
        self.hasDefended = True
        if self.defendCooldown != -1:
            self.defendCooldown = amount                            


    async def reset_all(self):
        if not self.player.game.active:
            return
        self.hasDefended = False
        
        if self.activateCooldown == 0:
            self.hasActivated = False
        elif self.activateCooldown != -1:
            self.activateCooldown -1
            
        if self.attackCooldown == 0:
            self.hasAttacked = False
        elif self.attackCooldown != -1:
            self.attackCooldown -= 1


    




# Goal cards
class GoalCard(NotPlayCard):
    async def check(self, phase, opponent):
        if phase >= 6:
            return False
        return await (self.before_defense,
                    self.after_defense,
                    self.before_play,
                    self.after_play,
                    self.before_attack,
                    self.after_attack,)[phase](opponent)
                  



    
    async def before_defense(self, opponent):
        print('before_defense')
        return False
    async def after_defense(self, opponent):
        print('after_defense')
        return False
    async def before_play(self, opponent):
        print('before_play')
        return False
    async def after_play(self, opponent):
        print('after_play')
        return False
    async def before_attack(self, opponent):
        print('before_attack')
        return False
    async def after_attack(self, opponent):
        print('after_attack')
        return False
    


class DanceOfMetal(GoalCard):
    async def after_attack(self, opponent):
        await self.player.remove_card_tags()
        await self.player.search_cards_in('play','legendary','swordsman',0)
        cards = await self.player.get_cards_with_tag('play',0)
        # TODO: fix parse_rp, it's broken
        print(len(cards),
              [c.rp >= await c.parse_rp(c.data['cost'])+15 for c in cards])
        return len(cards) > 0 and \
               any([c.rp >= await c.parse_rp(c.data['cost'])+15 for c in cards])
class FleshOfTheKing(GoalCard):
    async def after_attack(self, opponent):
        await self.player.remove_card_tags()
        await self.player.search_cards_in('play','legendary','demon',0)
        cards = await self.player.get_cards_with_tag('play',0)
        print(len(cards),
              [c.rp >= await c.parse_rp(c.data['cost'])+10 for c in cards])
        return len(cards) > 0 and \
               any([c.rp >= await c.parse_rp(c.data['cost'])+10 for c in cards])
class SmokelessLungs(GoalCard):
    async def after_attack(self, opponent):
        print(self.player.breath)
        return self.player.breath >= 20
class PowerOfAHomeowner(GoalCard):
    __slots__ = ('prevHp','attackingRP')
    async def before_defense(self, opponent):
        self.prevHp = self.player.health
        self.attackingRP = sum([a.rp for a in self.player.attackers])
        print('before_defense',self.prevHp,self.attackingRP)
        return False
    async def after_defense(self, opponent):
        print(self.attackingRP, self.player.health, self.prevHp)
        return self.attackingRP >= 25 and self.player.health == self.prevHp
class PrettyGoodAttack(GoalCard):
    async def after_attack(self, opponent):
        print(sum([a.rp for a in opponent.attackers]))
        return sum([a.rp for a in opponent.attackers]) >= 25
class NotTooBadStrength(GoalCard):
    async def after_attack(self, opponent):
        print(sum([a.rp if a is not None else 0 \
                        for a in self.player.play]))
        return sum([a.rp if a is not None else 0 \
                        for a in self.player.play]) >= 28
class TheMarchOfTheFairyfly(GoalCard):
    async def after_attack(self, opponent):
        print(len(list(filter(
                    lambda x: x is not None and x.rp <= 5,
                    self.player.play
                    ))))
        return len(list(filter(
                    lambda x: x is not None and x.rp <= 5,
                    self.player.play
                    ))) >= 8



# goal card list
goalCards = {
    'Dance of Metal':DanceOfMetal,
    'Flesh of the King':FleshOfTheKing,
    'Smokeless Lungs':SmokelessLungs,
    'Power of a Homeowner':PowerOfAHomeowner,
    'Pretty Good Attack':PrettyGoodAttack,
    'Not Too Bad Strength':NotTooBadStrength,
    'The March of the Fairlyfly':TheMarchOfTheFairyfly,
    }
async def make_goal_card(player, c):
    name = c.data['name']
    if name not in goalCards:
        return GoalCard(player, c)
    return goalCards[name](player, c)
