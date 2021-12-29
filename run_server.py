# main code -- this (will eventually) build and deploy the website, as well as set up all the different moving parts (card displayer, card game, quiz, etc.)


# ================ Style guide ================
# Functions: my_function()
# Classes: MyClass
# Instances: myInstance()
# 
# Socket messages follow these standards:
#   1. Client sends out a request (marked with a preceding 'req')
#   2. Server receives request, and handles it: handle_req_example_message()
#   3. Server may respond with a result (marked with a preceding 'res')
#   4. All messages are camel case: 'reqExampleMessage'
#   5. Messages sent from server which don't take a response are exceptions
#
# There is one exception to this standard, where the server sends out a
# request, and the client responds with a result. This is clearly marked.
#
# Card handling follows these standards:
#   1. Base cards, without any state associated, are called stock cards
#   2. Cards in play, with an associated state, are called play cards


import socketio
import os
from aiohttp import web
from server_scripts.CardManager import CardManager
from server_scripts.CardGameManager import CardGamePlayer
from server_scripts.QuizManager import QuizManager

### set up directories
# unchanging data
sourcedir         = "source"

# set up directories for data read/writes
# used by server
serverdatadir     = "server_data"
carddatadir       = f"{serverdatadir}/cards"
quizdatadir       = f"{serverdatadir}/quiz"
# used by client
deploymentdir     = "deployment"
clientdatadir     = "client_data"
clientdatadatadir = f"{clientdatadir}/data"
clientsocketdir   = f"{clientdatadir}/socket.io-client/dist"



### Set up server and sockets
# TODO: make sio a global?
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


### Set up internal server logic (manager classes)
cardManager = CardManager('/cards', carddatadir)
quizManager = QuizManager('/quiz', quizdatadir)
cardGamePlayer = CardGamePlayer('/cardgame', carddatadir, cardManager)
sio.register_namespace(cardManager)
sio.register_namespace(quizManager)
sio.register_namespace(cardGamePlayer)





# ================ Handle client requests ================

## card/deck managment stuff

# Handle client request for stock copy of all card data
# used to be reqAllCards
##@sio.on('reqAllStockCards')
### TODO: change to handle_reqAllStockCards
##async def handle_reqAllStockCards(sid, data):
##    await cardManager.resAllStockCards(sid, data)
##    
### Handle client request to add new card data (for 1 card) to database
### used to be clientAddCard
##@sio.on('reqAddStockCard')
##async def handle_reqAddStockCard(sid, data):
##    await cardManager.addStockCard(sid, data)
##
### used to be clientAddDeck
##@sio.on('reqAddDeck')
##async def handle_reqAddDeck(sid, data):
##    await cardManager.addDeck(sid, data)

# legacy chess stuff

@sio.on('reqLegacyChessChat')
async def handle_reqLegacyChessChat(sid, data):
    await sio.emit('resLegacyChessChat', data)

@sio.on('reqLegacyChessMovePiece')
async def handle_reqLegacyChessMovePiece(sid, data):
    await sio.emit('resLegacyChessMovePiece', data)
# ================ End handle client requests ================



### build website
# TODO: implement this



### deploy website
# Handle homepage requests
async def index(request):
    with open(f'./{deploymentdir}/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

# website html files
# let clients acccess anything in the deploymentdir as it appears in the filesystem
for directory in next(os.walk(f'./{deploymentdir}'))[1]:
    app.router.add_static(f'/{directory}', f'./{deploymentdir}/{directory}')

# misc. data files
app.router.add_static('/socket.io', clientsocketdir)
app.router.add_static('/data', clientdatadatadir)
app.router.add_get('/', index)


### Kick off server
if __name__ == '__main__':
    web.run_app(app, port=3000)

