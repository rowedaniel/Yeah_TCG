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

# set up directories for unchanging data
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



# Set up server and sockets
# TODO: make sio a global?
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


# Set up internal server logic (manager classes)
cardManager = CardManager(sio, carddatadir)
quizManager = QuizManager(sio, quizdatadir)
cardGamePlayer = CardGamePlayer(sio, carddatadir, cardManager)






# ================ Handle client requests ================
@sio.on('dong')
async def handle_recievePing(sid, data):
    print('dong')

# Handle client request for stock copy of all card data
# used to be reqAllCards
@sio.on('reqAllStockCards')
# TODO: change to handle_reqAllStockCards
async def handle_reqAllStockCards(sid, data):
    await cardManager.resAllStockCards(sid, data)
    
# Handle client request to add new card data (for 1 card) to database
# used to be clientAddCard
@sio.on('reqAddStockCard')
async def handle_reqAddStockCard(sid, data):
    await cardManager.addStockCard(sid, data)

# used to be clientAddDeck
@sio.on('reqAddDeck')
async def handle_reqAddDeck(sid, data):
    await cardManager.addDeck(sid, data)

# used to be clientReqDeck
@sio.on('reqQueueGame')
# TODO: change to handle_reqQueueGame
async def handle_reqQueueGame(sid, data):
    await cardGamePlayer.client_req_deck(sid,data)

# used to be playerGetCards
@sio.on('clientResChooseCards')
# TODO: change to handle_clientResChooseCards
async def handle_clientResChooseCards(sid, data):
    await cardGamePlayer.res_get_cards(sid, data)


@sio.on('startQuiz')
async def handle_startQuiz(sid, data):
    await quizManager.handle_startQuiz(sid, data)

@sio.on('quizAttemptAnswer')
async def handle_quizAttemptAnswer(sid, data):
    await quizManager.handle_quizAttemptAnswer(sid, data) 

@sio.on('quizSubmitQuestion')
async def handle_quizSubmitQuestion(sid, data):
    await quizManager.handle_quizSubmitQuestion(sid, data)

@sio.on('reqLegacyChessChat')
async def handle_reqLegacyChessChat(sid, data):
    await sio.emit('resLegacyChessChat', data)

@sio.on('reqLegacyChessMovePiece')
async def handle_reqLegacyChessMovePiece(sid, data):
    await sio.emit('resLegacyChessMovePiece', data)
# ================ End handle client requests ================


# ================ Handle client connects/disconnects ================
@sio.on('connect')
async def connect(sid, environ):
    print('connect', sid)

@sio.on('disconnect')
async def disconnect(sid):
    await cardGamePlayer.remove_player(sid)
    print('disconnect')
# ================ End handle client connects/disconnects ================





# Handle homepage requests
async def index(request):
    with open(f'./{deploymentdir}/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

# Handle client file requests
# website html files
for directory in next(os.walk(f'./{deploymentdir}'))[1]:
    app.router.add_static(f'/{directory}', f'./{deploymentdir}/{directory}')
# misc. data files
app.router.add_static('/socket.io', clientsocketdir)
app.router.add_static('/data', clientdatadatadir)
app.router.add_get('/', index)

# Kick off server
if __name__ == '__main__':

    
    async def pingAll():
        """Send out regular pings to all clients"""
        while True:
            await sio.sleep(20)
            print('dinging')
            await sio.emit('ding', {})
    
    sio.start_background_task(pingAll)
    web.run_app(app, port=3000)

