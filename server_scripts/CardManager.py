from server_scripts import loadCardStuff

class CardManager:
    def __init__(self,sio):
        self.cards = loadCardStuff.loadCards()
        self.decks = loadCardStuff.loadDecks()


        
        #bad practice, but not sure how to replace this
        self.sio = sio
    async def getCardByName(self, name):
        res = list(filter(lambda x: x['name']==name, self.cards))
        if len(res) > 0:
            return res[0]
        return False

    async def reqAllCards(self,sid,data):
        await self.sio.emit('resAllCards', self.cards, room=sid)
        

    

    async def clientAddCard(self,sid,data):
        print(data)
        self.cards.append(data)
        loadCardStuff.saveCard(data)

    async def clientAddDeck(self,sid,data):
        print(data)
        self.decks.append(data)
        loadCardStuff.saveDeck(data)

