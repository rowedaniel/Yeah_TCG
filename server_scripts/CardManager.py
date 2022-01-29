from socketio import AsyncServer

# TODO: change loadCardStuff to loadCardData
from server_scripts.card_loader.loadCardStuff import CardLoader
from server_scripts.Manager import Manager

# TODO: change to CardDataManager
# TODO: segregate so that all the stuff relating exclusively to cards is
# handled elsewhere
class CardManager(Manager):
    def __init__(self,
                 namespace : str,
                 datadir: str,
                 ):
        super().__init__(namespace, datadir)

        self.cardLoader = CardLoader(datadir)
        
        self.cards = self.cardLoader.loadCards()
        # TODO: check deck to make sure it works.
        self.decks = self.cardLoader.loadDecks()

        self.cardDefaults = {
            'name' : 'default',
            'cost' : 0,
            'img' : '',
            'move' : '',
            'txtcolor' : '',
            'cardType' : 'action',
            'cardAction' : '',
            'cardActionPlay' : '',
            'cardActionAttack' : '',
            'cardActionKill' : '',
            'cardActionDeath' : '',
        }
            
            

    async def getCardByName(self, name):
        res = list(filter(lambda x: x['name']==name, self.cards))
        if len(res) > 0:
            return res[0]
        return False

    async def cardQualityControl(self, card):
        for attr in card:
            if attr not in self.cardDefaults: 
                del card[attr]





    ### client request handling

    async def on_reqAllStockCards(self, sid, data):
        # NOTE: used to be resAllCards
        await self.emit('resAllStockCards', self.cards, room=sid)

        
             
            

    async def on_reqAddStockCard(self,sid,data):
        print(data)
        await self.cardQualityControl(data)
        self.cards.append(data)
        self.cardLoader.saveCards(self.cards)

    async def on_reqAddDeck(self,sid,data):
        print(data)
        # TODO: check deck to make sure it works.
        self.decks[data['name']] = {}
        self.decks[data['name']]['deck'] = data['deck']
        self.decks[data['name']]['goals'] = data['goals']
        self.cardLoader.saveDeck(data)

