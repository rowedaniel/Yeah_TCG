
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
    def __init__(self, player, card):
        super().__init__(player)
        self.data = card.data






# play cards
class PlayCard(NotPlayCard):
    __slots__ = ('rp',
                 'kills', 'attacks', 'defenses',
                 'hasDefended', 'hasActivated', 'hasAttacked')
    def __init__(self, player, card):
        super().__init__(player, card)
        # TODO: make this work with Roid Rage
        self.rp = self.parse_rp(self.data['cost'])

        
        self.hasDefended = False
        self.hasActivated = True # can't activate on first turn played
        self.hasAttacked = False

        # TODO: make it so that these get updated
        self.attacks = []  # attack successfully got through to player
        self.kills = []    # killed another card by attacking
        self.defenses = [] # defended agaisnt another card

    def parse_rp(self, coststr):
        return int(coststr)

    # all functions called by cards must not be async.
    async def set_rp(self, amount):
        if not self.player.game.active:
            return
        self.rp = self.parse_rp(amount)
        print('in set_rp, rp is:', self.rp)
        await self.player.game.cardGamePlayer.update_counters(
            self.player.game,
            self.player.socketId,
            'rp',
            [self.player.play.index(self), self.rp]
            )

    async def reset_rp(self):
        if not self.player.game.active:
            return
        # TODO: make this work with Roid Rage
        self.rp = self.parse_rp(self.data['cost'])


    async def add_attack(self):
        self.attacks.append(self.rp)
        
    async def add_kill(self, other):
        self.kills.append(other.data)

    async def add_defense(self, other):
        self.defenses.append(other.data)
    
                                                                                             
    async def update_rp(self, amount):
        if not self.player.game.active:
            return
        await self.set_rp(self.rp + self.parse_rp(amount))

    async def activate_cooldown(self, amount):
        if not self.player.game.active:
            return
        print('set activate cooldown for:',amount)
    async def attack_cooldown(self, amount):
        if not self.player.game.active:
            return
        print('set attack cooldown for:',amount)                                  


    async def reset_all(self):
        if not self.player.game.active:
            return
        self.hasDefended = False
        self.hasActivated = False
        self.hasAttacked = False


    




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
        print(len(cards),
              [c.rp >= c.parse_rp(c.data['cost'])+15 for c in cards])
        return len(cards) > 0 and \
               any([c.rp >= c.parse_rp(c.data['cost'])+15 for c in cards])
class FleshOfTheKing(GoalCard):
    async def after_attack(self, opponent):
        await self.player.remove_card_tags()
        await self.player.search_cards_in('play','legendary','demon',0)
        cards = await self.player.get_cards_with_tag('play',0)
        print(len(cards),
              [c.rp >= c.parse_rp(c.data['cost'])+10 for c in cards])
        return len(cards) > 0 and \
               any([c.rp >= c.parse_rp(c.data['cost'])+10 for c in cards])
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
        print(self.attackingRP, self.player.hp, self.prevHp)
        return self.attackingRP >= 25 and self.player.hp == self.prevHp
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
