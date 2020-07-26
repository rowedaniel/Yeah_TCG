import asyncio
from server_scripts import CardManager, CardGamePlayer


cardManager = CardManager.CardManager(None)
cardGamePlayer = CardGamePlayer.CardGamePlayer(None)
games = [CardGamePlayer.Game(cardManager, cardGamePlayer) for i in range(4)]




async def testGame(num):
    
    await games[num].start_new(0,0,'j','j')
    print('\n\n\n\nmade game', num)
    
    print('running game', num)
    for i in range(10):
        await games[num].run_turn()
    print('finished running game', num)

async def main():
    task1 = asyncio.create_task(testGame(0))
    await task1

asyncio.run(main())
