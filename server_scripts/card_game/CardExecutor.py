import random



collectionNames = ('hand','discard','play','deck','activeGoals',
                   'goals',)
rarities = ('common','rare','legendary','any')
unitTypes = ('demon','swordsman','Jaycob','any')
tags = [str(i) for i in range(10)]

conditionalCommands = (
                      'randomChance',
                      'checkCardsTag',
                      'decide',
                      'checkBreath',
                 )
variableCommands = ('setRandomChance',
                    )

cmdTable = {
    'increaseBreath':(
                'update_breath(',
                2,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in [str(i) for i in range(-5,5)],
                lambda x,y: x+y+')')
                  ),



    # conditional commands

    # TODO: finish this
    # if it succeeds, then execute the next command.
    # Else, skip next command.
    'randomChance':(
                'check_random_chance(memory,',
                1,
                (lambda x: x in [str(i) for i in range(1,10)],
                lambda x,y: x+y+')'),
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

    'checkBreath':(
                'checkBreath(',
                2,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in [str(i) for i in range(0,10)],
                lambda x,y: x+y+')'),
            ),


    
    # tags the top x cards of a collection
    'spyCollection':(
                'spy_cards_from(',
                4,
                (lambda x: x in ('me','you'),
                lambda x,y: y+'.'+x),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)),
                (lambda x: x in [str(i) for i in range(0,10)],
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





    # variable commands store numbers in the designated variable
    # updates the current random number
    'setRandomChance':(
                'get_random_number(',
                1,
                (lambda x: x in [str(i) for i in range(1,40)],
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
                (lambda x: x in [str(i) for i in range(-40,40)],
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
                'miyamoto_musashi(',
                4,
                (lambda x: x in ('me','you'),
                lambda x,y: x+y+','),
                (lambda x: x in ('me','you'),
                lambda x,y: x+y+','),
                (lambda x: x in collectionNames,
                lambda x,y: x+repr(y)+','),
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

async def execute_card_action(card, action, me, you):
    c = card.data[action].rstrip().split(' ')
    i = 0
    cmdStr = ''
    currentCommand = ''
    skipCommand = False
    currentArgIndex = 0
    memory = 0


    await me.remove_card_tags()
    await you.remove_card_tags()
    if any([len(c.tags)>0 for _,c in await me.get_existing_cards(me.play)]):
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
                if skipCommand:
                    print('waiting to skip')
            elif currentCommand in variableCommands:
                memory = await eval(cmdStr)
                print('memory is:', memory)
            else:
                print('running command:',cmdStr)
                await eval(cmdStr)
            cmdStr = ''
            currentCommand = ''
            currentArgIndex = 0
        i += 1







async def miyamoto_musashi(player1, player2, collection, tag):
    await player1.increase_rp(
        len(await player2.get_existing_cards(player2.collections[collection])),
        tag)

# conditional funcs

async def check_random_chance(actual, success):
    print('in check_random_chance, actual =',actual,
          'success =',success,
          'returning: ', actual == success)
    return actual == success

async def get_random_number(possibilities):
    a = random.randint(1, possibilities)
    print(a)
    return a












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
        await execute_card_action(card,
                                     p1,
                                     p2)
    

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
