from aiohttp import web
import socketio
from server_scripts import CardManager, CardGamePlayer 

# creates a new Async Socket IO Server
sio = socketio.AsyncServer()
# Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
# instance
sio.attach(app)


# Server Logic Stuff
cardManager = CardManager.CardManager(sio)
cardGamePlayer = CardGamePlayer.CardGamePlayer(sio, cardManager)



# need to have this?
async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


# background task stuff
async def pingAll():
    while True:
        await sio.sleep(20)
        print('dinging')
        await sio.emit('ding', {})



# requests and stuff

@sio.on('dong')
async def recievePing(sid, data):
    print('dong')

    

@sio.on('reqAllCards')
async def reqAllCards(sid, data):
    await cardManager.reqAllCards(sid,data)

@sio.on('clientAddCard')
async def clientAddCard(sid, data):
    await cardManager.clientAddCard(sid,data)

@sio.on('clientAddDeck')
async def clientAddDeck(sid, data):
    await cardManager.clientAddDeck(sid,data)

@sio.on('clientReqDeck')
async def clientReqDeck(sid, data):
    await cardGamePlayer.client_req_deck(sid,data)

@sio.on('playerGetCards')
async def playerGetCards(sid, data):
    await cardGamePlayer.res_get_cards(sid, data)


    
@sio.on('connect')
async def connect(sid, environ):
    print('connect', sid)


@sio.on('disconnect')
async def disconnect(sid):
    await cardGamePlayer.remove_player(sid)
    print('disconnect')

# We bind our aiohttp endpoint to our app
# router

app.router.add_static('/data', './data')
app.router.add_static('/socket.io', './node_modules/socket.io-client/dist')
app.router.add_get('/', index)

# We kick off our server
if __name__ == '__main__':
    sio.start_background_task(pingAll)
    web.run_app(app, port=3000)

