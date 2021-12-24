from socketio import AsyncServer

class Manager:
    def __init__(self,
                 sio : AsyncServer,
                 datadir: str,
                 ):
        # TODO: add documentation here
        
        self.sio = sio
        self.datadir = datadir
        
