from threading import Thread
from pywebhost import PyWebHost
from pywebhost.handler import Request
from pywebhost.modules import WriteContentToRequest,BinaryMessageWrapper
from pywebhost.modules.websocket import WebsocketSession, WebsocketSessionWrapper
import keyboard,time,socket,json,queue
def setupQueue(initalizer):
    q = queue.LifoQueue()
    for item in initalizer[::-1]:q.put(item)
    return q

keyMaps = ["asdf","hjkl"]
keyFree = [setupQueue(_) for _ in keyMaps]
keyHeld = [queue.LifoQueue() for _ in keyMaps]

def get_ip():
    # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:        
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class Session(WebsocketSession):    
    def onOpen(self, request=None, content=None):
        super().onOpen(request, content)
        self.send(json.dumps({'keymaps':keyMaps}))

    def onReceive(self, frame: bytearray):    
        press, index = frame[0] >= 255,int(frame[1])
        if press and keyFree[index].not_empty:
            key = keyFree[index].get()
            keyHeld[index].put(key)            
            keyboard.press(key)            
        elif not press and keyHeld[index].not_empty:
            key = keyHeld[index].get()
            keyFree[index].put(key)
            keyboard.release(key)

server = PyWebHost(('0.0.0.0',3300))    
@server.route('/ws')
@WebsocketSessionWrapper()
def ws(initator,request: Request, content):
    return Session
@server.route('/')
@BinaryMessageWrapper(read=False)
def index(initator,request: Request, content):
    request.send_response(200)
    return open('index.html',encoding='utf-8').read() if not 'page' in globals() else page
def displayKeys():
    lastDisplay = ''
    while True:
        combined = []
        for n in range(0,len(keyMaps)):
            for k in keyMaps[n]:
                disp = k.upper() if k in keyHeld[n].queue else k.lower()
                combined.append(disp)            
        finalDisplay = ' '.join(combined)
        if finalDisplay != lastDisplay:
            print(end=finalDisplay + '\r')
        lastDisplay = finalDisplay
        time.sleep(0.01)
tDisp = Thread(target=displayKeys,name='KeyUpdater',daemon=True)
tDisp.start()
URL = f'http://{get_ip()}:{server.server_address[1]}'
import ctypes
ctypes.windll.kernel32.SetConsoleTitleW("wsKeyboard @ "+URL)
print('局域网连接:',URL)
server.serve_forever()
