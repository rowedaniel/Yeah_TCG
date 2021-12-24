from socketio import AsyncServer

# TODO: change loadCardStuff to loadCardData
from server_scripts.card_loader.loadCardStuff import CardLoader
from server_scripts.Manager import Manager

# TODO: change to CardDataManager
# TODO: segregate so that all the stuff relating exclusively to cards is
# handled elsewhere
class CardManager(Manager):
    def __init__(self,
                 sio : AsyncServer,
                 datadir: str,
                 ):
        super().__init__(sio, datadir)

        self.cardLoader = CardLoader(datadir)
        
        self.cards = self.cardLoader.loadCards()
        # TODO: check deck to make sure it works.
        self.decks = self.cardLoader.loadDecks()

    async def getCardByName(self, name):
        res = list(filter(lambda x: x['name']==name, self.cards))
        if len(res) > 0:
            return res[0]
        return False

    async def resAllStockCards(self, sid, data):
        # used to be resAllCards
        await self.sio.emit('resAllStockCards', self.cards, room=sid)
        


    async def cardQualityControl(self, card):
        for attr in card:
            if attr not in (
                            'name',
                            'cost',
                            'img',
                            'move',
                            'txtcolor',
                            'cardType',
                            'cardAction',
                            ):
                del card[attr]

                
        if 'name' not in card:
            card['name'] = 'default'
            
        if 'cost' not in card:
            cards['cost'] = '0'
        if cards['cost'] != 'X':
            try:
                int(cards['cost'])
            except ValueError:
                cards['cost'] = '0'

        if 'img' not in card:
            card['img'] = ''
        
        if 'move' not in card:
            card['move'] = ''
        
        if 'txtcolor' not in card:
            card['txtcolor'] = ''
        
        if 'cardType' not in card:
            card['cardType'] = 'action'
        
        if 'cardAction' not in card:
            card['cardAction'] = ''
        
             
            

    async def addStockCard(self,sid,data):
        print(data)
        await self.cardQualityControl(data)
        self.cards.append(data)
        self.cardLoader.saveCards(self.cards)

    async def addDeck(self,sid,data):
        print(data)
        # TODO: check deck to make sure it works.
        self.decks[data['name']] = {}
        self.decks[data['name']]['deck'] = data['deck']
        self.decks[data['name']]['goals'] = data['goals']
        self.cardLoader.saveDeck(data)

