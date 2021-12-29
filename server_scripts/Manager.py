from socketio import AsyncServer
from socketio import AsyncNamespace

class Manager(AsyncNamespace):
    def __init__(self,
                 namespace : str,
                 datadir: str,
                 ):
        # TODO: add documentation here

        super().__init__(namespace)
        self.datadir = datadir
        
