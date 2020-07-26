

async def execute_card_action(card, index, me, you):
    cmdTable = {
    'increaseBreath':(2,
                  (lambda x: x in ('me','you'),
                   lambda x,y: y+'.'+x),
                  (lambda x: x in ('1','2','3'),
                   lambda x,y: x+'('+y+')')
                      ),
    'increaseRP':(2,
                  (lambda x: x in ('this',),
                   lambda x,y: 'card.'+x), # <-- this gotta be changed
                  (lambda x: x in [str(i) for i in range(1,10)],
                   lambda x,y: x+'('+y+')')
                  ),
    'dealCards':(2,
                  (lambda x: x in ('me', 'you',),
                   lambda x,y: y+'.'+x),
                  (lambda x: x in [str(i) for i in range(1,10)],
                   lambda x,y: x+'('+y+')')
                ),
    'searchDeckCategory':(4,
                  (lambda x: x in ('me', 'you'),
                   lambda x,y: x),
                  (lambda x: x in [str(i) for i in range(1,10)],
                   lambda x,y: x),
                  (lambda x: x in ('common', 'rare', 'legendary'),
                   lambda x,y: repr(x)),
                  (lambda x: x in ('swordsman', 'demon'),
                   lambda x,y: repr(x)),
                ),
            }

    c = card.data['cardAction'].rstrip().split(' ')
    print('parsing command list',c)
    i = 0
    cmdStr = ''
    currentCommand = ''
    currentArgIndex = 0

    while i < len(c):

        #commands
        if c[i] == 'increaseBreath':
            currentCommand='increaseBreath'
            currentArgIndex = 0
            cmdStr = 'increase_breath'

        elif c[i] == 'increaseRP':
            currentCommand = 'increaseRP'
            currentArgIndex = 0
            cmdStr = 'increase_rp'

        elif c[i] == 'drawCards':
            currentCommand = 'dealCards'
            currentArgIndex = 0
            cmdStr = 'deal_cards'


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
            print('running command:',cmdStr)
            await eval(cmdStr)
        
        i += 1
