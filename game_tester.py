import asyncio
##from server_scripts import CardManager, CardGamePlayer


##cardManager = CardManager.CardManager(None)
##cardGamePlayer = CardGamePlayer.CardGamePlayer(None)
##games = [CardGamePlayer.Game(cardManager, cardGamePlayer) for i in range(4)]




##async def testGame(num):
##    
##    await games[num].start_new(0,0,'j','j')
##    print('\n\n\n\nmade game', num)
##    
##    print('running game', num)
##    for i in range(10):
##        await games[num].run_turn()
##    print('finished running game', num)

async def func_1(a):
    return (await a) +1

async def func_2(b):
    return b+1

async def test_exec():
    return ('hi', 'bye') in ['hi','bye']

async def main():
    task1 = asyncio.create_task(test_exec())
    print(await task1)

asyncio.run(main())
