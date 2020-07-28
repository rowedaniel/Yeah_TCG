
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

#async
def execute_card_action(card, index, me, you):
    collectionNames = ('hand','discard','play','deck','activeGoals',
                       'goals',)
    rarities = ('common','rare','legendary','any')
    unitTypes = ('demon','swordsman','jaycob','any')

    continuousCommands = ('spyCollection',
                          'topCollection',
##                          'searchCollectionName',
                          'searchCollection',
                          'reveal',
                          'this',
                          )
    modifyCommands = (
                          'randomChance',
                     )
    
    cmdTable = {
    'increaseBreath':(2,
                  (lambda x: x in ('me','you'),
                   lambda x,y: y+'.'+x),
                  (lambda x: x in ('1','2','3'),
                   lambda x,y: x+'('+y+')')
                      ),
    # gets a copy of the top x cards, and returns them
    'spyCollection':(3,
                  (lambda x: x in ('me','you'),
                   lambda x,y: y+'.'+x),
                  (lambda x: x in [str(i) for i in range(10)],
                   lambda x,y: x+'('+y),
                  (lambda x: x in collectionNames,
                   lambda x,y: x+','+repr(y)+'))'),
                     ),
    # get the top x cards of collection, and returns them
    'topCollection':(3,
                  (lambda x: x in ('me','you'),
                   lambda x,y: y+'.'+x),
                  (lambda x: x in [str(i) for i in range(10)],
                   lambda x,y: x+'('+y),
                  (lambda x: x in collectionNames,
                   lambda x,y: x+','+repr(y)+'))'),
                     ),
    # searches for card name, and then returns cards
    # TODO: fix this, it won't work because no spaces
##    'searchCollectionName':(3,
##                  (lambda x: x in ('me','you'),
##                   lambda x,y: y+'.'+x),
##                  (lambda x: x in collectionNames,
##                   lambda x,y: x+'(me.'+y),
##                  (lambda x: x in cardNames,
##                   lambda x,y: x+','+repr(y)+')'),
##                     ),
    # searches for category, and then returns cards
    'searchCollection':(4,
                  (lambda x: x in ('me','you'),
                   lambda x,y: y+'.'+x),
                  (lambda x: x in rarities,
                   lambda x,y: x+'('+repr(y)),
                  (lambda x: x in unitTypes,
                   lambda x,y: x+','+repr(y)),
                  (lambda x: x in collectionNames,
                   lambda x,y: x+','+repr(y)+'))'),
                     ),
    
    # reveals result of previous command, then returns same list
    'reveal':(0,),

    
    # returns this card
    'this':(0,),

    
    # if it succeeds, then execute the next command.
    # Else, skip next command.
    'randomChance':(2,
                    (lambda x: x in [str(i) for i in range(1,10)],
                     lambda x,y: x+'('+repr(y)),
                    (lambda x: x in [str(i) for i in range(2,11)],
                     lambda x,y: x+','+repr(y)+')'),
                    ),

    
    # adds result of previous command to collection
    'addToCollection':(4,
                  (lambda x: x in ('me','you'),
                   lambda x,y: y+'.'+x),
                  (lambda x: x in collectionNames,
                   lambda x,y: x+'(me.'+y)
                       ),
    
    # queries player as input of previous command
    'choose':(1,
                  (lambda x: x in ('me','you'),
                   lambda x,y: y+'.'+x),
              ),

    # sets rp to x
    'setRP':(1,
                  (lambda x: x in [str(i) for i in range(1,40)],
                   lambda x,y: x+'('+repr(y)+')'),
             ),
    # increase rp by x
    'increaseRP':(1,
                  (lambda x: x in [str(i) for i in range(1,40)],
                   lambda x,y: x+'('+repr(y)+')'),
             ),



    # sets the cooldown to activate card
    'activateCooldown':(1,
                  (lambda x: x in [str(i) for i in range(-1,5)],
                   lambda x,y: x+'('+repr(y)+')'),
             ),
    # sets the cooldown to attack with card
    'attackCooldown':(1,
                  (lambda x: x in [str(i) for i in range(-1,5)],
                   lambda x,y: x+'('+repr(y)+')'),
             ),
    


    # TODO: how to do activate cards?
    
            }

    c = card.data['cardAction'].rstrip().split(' ')
    print('parsing command list',c)
    i = 0
    cmdStr = ''
    currentCommand = ''
    prevCommand = ''
    prevCommandStr = ''
    currentArgIndex = 0

    while i < len(c):

        print('new arg/command:', c[i])
        #commands
        if c[i] == 'increaseBreath':
            currentCommand=c[i]
            currentArgIndex = 0
            cmdStr = 'update_breath'

        elif c[i] == 'spyCollection':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'spy_collection'

        elif c[i] == 'topCollection':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'pull_cards_from'

        elif c[i] == 'searchCollection':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'search_cards_in'

        elif c[i] == 'reveal':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'disp_cards('

        elif c[i] == 'this':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'card)'

        # TODO: implement this
##        elif c[i] == 'randomChance':
##            currentCommand = c[i]
##            currentArgIndex = 0
##            cmdStr = 'spy_collection'

        elif c[i] == 'addToCollection':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'add_cards_to'

        elif c[i] == 'choose':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'choose_cards('

        elif c[i] == 'setRP':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'set_rp'

        elif c[i] == 'increaseRP':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'increase_rp'

        elif c[i] == 'activateCooldown':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'set_activate_cooldown'

        elif c[i] == 'attackCooldown':
            currentCommand = c[i]
            currentArgIndex = 0
            cmdStr = 'set_attack_cooldown'


        # args
        else:
            if len(currentCommand) > 0 and \
               currentCommand in cmdTable and \
               currentArgIndex < cmdTable[currentCommand][0] and \
               cmdTable[currentCommand][currentArgIndex+1][0](c[i]):

                cmdStr = cmdTable[currentCommand][currentArgIndex+1][1](
                    cmdStr,c[i])
                #cmdStr += ','

                currentArgIndex += 1
            else:
                cmdStr = ''
                currentCommand = ''
                currentArgIndex = 0

        if len(currentCommand) > 0 and \
           currentCommand in cmdTable and \
           currentArgIndex >= cmdTable[currentCommand][0]:
            if currentCommand not in continuousCommands:
                print('running command:',cmdStr+prevCommandStr)
                #await eval(cmdStr)
                #print(cmdStr)
                prevCommandStr = ''
            prevCommandStr = cmdStr + prevCommandStr
            prevCommand = currentCommand
            cmdStr = ''
        else:
            print('failed')
            print(len(currentCommand))
            print(currentCommand)
            print(cmdTable[currentCommand][0])
        print('current command str', cmdStr)
        i += 1


class TestCard:
    def __init__(self, cardAction):
        self.data = {'cardAction':cardAction}


def main():
    testCards = [
        TestCard('increaseBreath me 3'),
        TestCard('spyCollection you 3 hand choose me'),
        TestCard('topCollection me 3 deck choose you'),
        TestCard('searchCollection you rare jaycob play choose me'),
        TestCard('this choose me reveal choose me'),
        TestCard('this choose me'),
        ]

    for t in testCards:
        execute_card_action(t, 0, 0, 0)
        print()

if __name__ == '__main__':
    main()
