import random



collectionNames = ('hand','discard','play','deck','activeGoals',
                   'goals',)
rarities = ('common','rare','legendary','any')
unitTypes = ('demon','swordsman','Jaycob','any')
tags = [str(i) for i in range(10)]

conditionalCommands = (
                      'randomChance',
                      'checkCardsTag',
                      'decide'
                 )
OnStr = ('onPlay',
         'onAttack',
         'onKill')

cmdTable = {
    'increaseBreath':(
                'update_breath(',
                2,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in ('1','2','3'),
                lambda x,y: x+y+')')
                  ),



    # conditional commands

        # TODO: finish this
    # if it succeeds, then execute the next command.
    # Else, skip next command.
    'randomChance':(
                'random_chance(',
                2,
                (lambda x: x in [str(i) for i in range(1,10)],
                lambda x,y: x+y),
                (lambda x: x in [str(i) for i in range(2,11)],
                lambda x,y: x+','+y+')'),
            ),

    'checkCardsTag':(
                'check_cards_tag(',
                4,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)),
                (lambda x: x in [str(i) for i in range(1,10)],
                lambda x,y: x+','+y),
                (lambda x: x in tags,
                lambda x,y: x+','+repr(y)+')'),
            ),

    'decide':(
                'decide()',
                1,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
            ),



    
    # tags the top x cards of a collection
    'spyCollection':(
                'spy_cards_from(',
                4,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)),
                (lambda x: x in [str(i) for i in range(-1,10)],
                lambda x,y: x+','+y),
                (lambda x: x in tags,
                lambda x,y: x+','+y+')'),
            ),

    # searches collection for card of x rarity y type, and tags
    'searchCollection':(
                'search_cards_in(',
                5,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)),
                (lambda x: x in rarities,
                lambda x,y: x+','+repr(y)),
                (lambda x: x in unitTypes,
                lambda x,y: x+','+repr(y)),
                (lambda x: x in tags,
                lambda x,y: x+','+y+')'),
            ),

    
    # returns this card
    'this':(
                'card.add_tag(',
                1,
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),






    # result commands

    
    # adds tagged cards to collection
    'moveCards':(
                'move_cards(',
                4,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)+','),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)+','),
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),

    # sets rp to x
    'setRP':(
                'set_rp(',
                3,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in [str(i) for i in range(0,40)],
                lambda x,y: x+y+','),
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),
    # reset rp to default
    'resetRP':(
                'reset_rp(',
                2,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),
    # increase rp by x
    'increaseRP':(
                'increase_rp(',
                3,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in [str(i) for i in range(1,40)],
                lambda x,y: x+y+','),
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),

    'roidRage':(
                'increase_rp(',
                2,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in tags,
                lambda x,y: x+'card.rp,'+y+')'),
            ),

    'miyamotoMusashi':(
                'increase_rp(',
                4,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in ('me','you'),
                lambda x,y: x+'len('+y+'.collections['),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)+']),'),
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),
    
                



    # sets the cooldown to activate card
    'activateCooldown':(
                'set_activate_cooldown(',
                3,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in [str(i) for i in range(-1,40)],
                lambda x,y: x+y+','),
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),
    # sets the cooldown to attack with card
    'attackCooldown':(
                'set_attack_cooldown(',
                3,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in [str(i) for i in range(-1,40)],
                lambda x,y: x+y+','),
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),
    # sets the cooldown to defend with card
    'defendCooldown':(
                'set_defend_cooldown(',
                3,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in [str(i) for i in range(-1,40)],
                lambda x,y: x+y+','),
                (lambda x: x in tags,
                lambda x,y: x+y+')'),
            ),





    # commands that are both continuous and result

     # reveals result of previous command, then returns same list
    'reveal':(
                'disp_cards(',
                4,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in ('me','you'),
                lambda x,y: x+y),
                (lambda x: x in collectionNames,
                lambda x,y: x+','+repr(y)),
                (lambda x: x in tags,
                lambda x,y: x+','+y+')'),
            ),

    
    
    # queries player as input of previous command
    'choose':(
                'choose_cards(',
                6,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in ('me','you'),
                lambda x,y: x+y),
                (lambda x: x in collectionNames,
                lambda x,y: x+','+repr(y)),
                (lambda x: x in [str(i) for i in range(-1,20)],
                lambda x,y: x+','+y),
                (lambda x: x in tags,
                lambda x,y: x+','+y),
                (lambda x: x in tags,
                lambda x,y: x+','+y+')'),
            ),

    'removeTag':(
                'remove_card_tags_with_tag(',
                4,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)),
                (lambda x: x in tags,
                lambda x,y: x+','+y),
                (lambda x: x in tags,
                lambda x,y: x+','+y+')'),
            ),
                


    # TODO: how to do activate cards?
    
            }


##cardNames = []

async def get_unit_card_special(card):
    # check if card has any special stuff
    c = card.data['cardAction'].rstrip().split(' ')
    cmdTable = {
        'after':(1,
                 (lambda x: x in [str(i) for i in range(1,5)],
                  lambda x,y: int(y))
                 ),
        'onPlay':(0,),
        }

    out = []
    if len(c) > 0 and \
       c[0] in cmdTable:
        out.append(c[0])
        cmdStr = c[0]
        for i in range(cmdTable[c[0]][0]):
            if cmdTable[c[0]][i+1][0](c[i+1]):
                out.append(cmdTable[c[0]][i+1][1](cmdStr, c[i+1]))
            else:
                return []
    return out

async def execute_card_action(card, me, you):
    c = card.data['cardAction'].rstrip().split(' ')
    i = 0
    cmdStr = ''
    currentCommand = ''
    skipCommand = False
    currentArgIndex = 0


    await me.remove_card_tags()
    await you.remove_card_tags()
    if any([len(c.tags)>0 for c in me.play]):
        print('tags not reset!!')

    
    while i < len(c):

        print('new arg/command:', c[i])
        # commands
        if c[i] in cmdTable:
            currentCommand = c[i]
            cmdStr = cmdTable[c[i]][0]
        # args
        elif len(currentCommand) > 0 and \
           currentCommand in cmdTable and \
           currentArgIndex < cmdTable[currentCommand][1] and \
           cmdTable[currentCommand][currentArgIndex+2][0](c[i]):

            cmdStr = cmdTable[currentCommand][currentArgIndex+2][1](
                cmdStr,c[i])
            currentArgIndex += 1
        elif c[i] in OnStr:
            # not the right time to do it
            skipCommand = True
        # error
        else:
            cmdStr = ''
            currentCommand = ''
            currentArgIndex = 0
            print('failed command!')

        if len(currentCommand) > 0 and \
           currentCommand in cmdTable and \
           currentArgIndex >= cmdTable[currentCommand][1]:
            if skipCommand:
                skipCommand = False
                print('skip')
            elif currentCommand in conditionalCommands:
                skipCommand = await eval(cmdStr)
                print('waiting to skip')
            else:
                print('running command:',cmdStr)
                await eval(cmdStr)
            cmdStr = ''
            currentCommand = ''
            currentArgIndex = 0
        i += 1





async def execute_card_action_on(card, me, you, onStrIndex):
    c = card.data['cardAction'].rstrip().split(' ')
    i = 0
    cmdStr = ''
    currentCommand = ''
    skipCommand = False
    currentArgIndex = 0
    onStr = OnStr[onStrIndex]
    onConditionSatisfied = False

    await me.remove_card_tags()
    await you.remove_card_tags()
    if any([len(c.tags)>0 for c in me.play]):
        print('tags not reset!!')

    
    while i < len(c):
        print('new arg/command:', c[i])
        # commands
        if c[i] in cmdTable:
            currentCommand = c[i]
            cmdStr = cmdTable[c[i]][0]
        # args
        elif len(currentCommand) > 0 and \
           currentCommand in cmdTable and \
           currentArgIndex < cmdTable[currentCommand][1] and \
           cmdTable[currentCommand][currentArgIndex+2][0](c[i]):

            cmdStr = cmdTable[currentCommand][currentArgIndex+2][1](
                cmdStr,c[i])
            currentArgIndex += 1
        elif c[i] == onStr:
            onConditionSatisfied = True
            print('condition satisfied')
        # error
        else:
            cmdStr = ''
            currentCommand = ''
            currentArgIndex = 0
            print('failed command!')

        if len(currentCommand) > 0 and \
           currentCommand in cmdTable and \
           currentArgIndex >= cmdTable[currentCommand][1]:
            if skipCommand:
                skipCommand = False
                print('skip')
            elif currentCommand in conditionalCommands:
                skipCommand = await eval(cmdStr)
                print('waiting to skip')
            elif onConditionSatisfied:
                onConditionSatisfied = False
                print('running command:',cmdStr)
                await eval(cmdStr)
            cmdStr = ''
            currentCommand = ''
            currentArgIndex = 0
        i += 1






# conditional funcs

async def random_chance(success, total):
    return random.randint(1,total) <= success







async def main():

    
    class TestCard:
        def __init__(self, cardAction):
            self.data = {'cardAction':cardAction}
        async def add_tag(self, tag):
            pass

    class TestPlayer:
        def __init__(self):
            self.play = []
        async def remove_card_tags(self):
            pass
        async def increase_breath(self, amount):
            pass
        async def set_attack_cooldown(self, duration, tag):
            pass
    
    testCards = [
        TestCard('onPlay this 0 onPlay attackCooldown me -1 0 '+\
                 'increaseBreath me 1'),
        ]
    p1 = TestPlayer()
    p2 = TestPlayer()
    for card in testCards:
        await execute_card_action_on(card,
                                     p1,
                                     p2,
                                     0)
    

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
