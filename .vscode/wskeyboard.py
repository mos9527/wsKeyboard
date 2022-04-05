from pywebhost import PyWebHost
from pywebhost.handler import Request
from pywebhost.modules import WriteContentToRequest
from pywebhost.modules.websocket import WebsocketSession, WebsocketSessionWrapper
import keyboard,time
class DefaultDict(dict):
    def __init__(self,default_val):
        self.default_val = default_val
        super().__init__()
    def __getitem__(self, k):
        if not k in self:
            self[k] = self.default_val
        return super().__getitem__(k)
        
class KeyState(dict):
    def __init__(self):
        self.k_state = DefaultDict(default_val=False)
        super().__init__()

    def handle(self):
        for k in self:
            if self[k] > 0:                
                if not self.k_state[k]:keyboard.press(k)
                self.k_state[k] = True
            else:
                self.k_state[k] = False
                keyboard.release(k)

    def __setitem__(self, k,v):        
        if not k in self:super().__setitem__(k, 0)
        super().__setitem__(k, self[k] + (1 if v == '↓' else -1))
        return self.handle()

class Session(WebsocketSession):
    def __init__(self, request, raw_frames, *a, **k):
        self.keyState = KeyState()
        self.ping_ts  = 0
        super().__init__(request, raw_frames=raw_frames, *a, **k)
    
    def onOpen(self):        
        self.ping_ts = time.time()
        self.send('ping')
    
    def onReceive(self, frame: bytearray):    
        message = frame.decode()        
        verb,key = message.split()                       
        if verb in {'↓','↑'}:
            self.keyState[key] = verb
        elif self.ping_ts:
            print(self.session_id,'connected, estimated delay: %fms'%((time.time() - self.ping_ts)*1000))
server = PyWebHost(('0.0.0.0',3300))    

@server.route('/ws')
@WebsocketSessionWrapper()
def ws(initator,request: Request, content):
    return Session

@server.route('/')
def index(initator,request: Request, content):
    WriteContentToRequest(request,'index.html',mime_type='text/html')

print(f'Serving...http://localhost:{server.server_address[1]}')
server.serve_forever()
