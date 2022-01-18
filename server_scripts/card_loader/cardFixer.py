from server_scripts.CardManager import CardManager
from server_scripts.card_loader.loadCardStuff import CardLoader

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
OnStr = ('onPlay',
         'onAttack',
         'onKill')

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


async def execute_card_action(cardAction):
    c = cardAction.rstrip().split(' ')
    i = 0


    commands = {'default':[]}
    currentOnStr = 'default'

    for s in OnStr:
        commands[s] = []

    
    currentCommand = ''
    skipCommand = False
    currentArgIndex = 0

    
    while i < len(c):
        
        # commands
        if c[i] in cmdTable:
            currentCommand = c[i]
            commands[currentOnStr].append(c[i])
            
        # args
        elif len(currentCommand) > 0 and \
           currentCommand in cmdTable and \
           currentArgIndex < cmdTable[currentCommand][1] and \
           cmdTable[currentCommand][currentArgIndex+2][0](c[i]):
            currentArgIndex += 1
            
            commands[currentOnStr].append(c[i])
            
        elif c[i] in OnStr:
            currentOnStr = c[i]
            
        # error
        else:
            currentCommand = ''
            currentOnStr = 'default'
            currentArgIndex = 0


        if len(currentCommand) > 0 and \
           currentCommand in cmdTable and \
           currentArgIndex >= cmdTable[currentCommand][1]:
            currentCommand = ''
            currentOnStr = 'default'
            currentArgIndex = 0

            

        
        i += 1

    return commands





async def miyamoto_musashi(player1, player2, collection, tag):
    await player1.increase_rp(
        len(await player2.get_existing_cards(player2.collections[collection])),
        tag)

# conditional funcs

async def check_random_chance(actual, success):

    return actual == success

async def get_random_number(possibilities):
    a = random.randint(1, possibilities)
    return a






async def main():
    
    
    m = CardManager('asdf', 'server_data/cards')
    cl = CardLoader('server_data/cards')

    for c in m.cards:
        action = await execute_card_action(c['cardAction'])
        c['cardAction']         = ' '.join(action['default'])
        c['cardActionOnPlay']   = ' '.join(action['onPlay'])
        c['cardActionOnAttack'] = ' '.join(action['onAttack'])
        c['cardActionOnKill']   = ' '.join(action['onKill'])

    cl.saveCards(m.cards)
        

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
