import websockets
from sys import stderr
from json import dumps

RESET = "\033[0m"
RED = "\033[31m"

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.messages = []
        self.autorisedUsers = None


    async def connect(self):
        self.websocket = await websockets.connect(self.url)
        if self.autorisedUsers:
            await self.sendUserJoin(self.autorisedUsers)
        print("Game instance connected to", self.url, file=stderr)

    async def receive_messages(self):
        try:
            async for message in self.websocket:
                self.messages.append(message)
        except:
            pass

    """Client to game serv
    char 0 = player number
    char 1 : u = up, d = down
    """
    def getMsg(self):
        msg = []
        msg = self.messages.copy()
        self.messages.clear()
        return msg

    async def sendMsg(self, msg):
        while True:
            try:
                await self.websocket.send(dumps(msg))
                break
            except:
                await self.connect()

    async def sendUserJoin(self, msg):
        try:
            self.autorisedUsers = msg
            await self.websocket.send("autorisedusers" + dumps(msg))
        except:
            pass

    async def sendEndGame(self, msg, gameError=False):
        if gameError:
            game = {
                "ballx" : 0, # -0.5 -> 0.5
                "bally" : 0, # -0.5 -> 0.5
                "p1" : 0, # -0.5 -> 0.5
                "p2" : 0, # -0.5 -> 0.5
                "p3" : 0, # -0.5 -> 0.5
                "p4" : 0, # -0.5 -> 0.5
                "state" : "game_over",
                "score1" : 0,
                "score2" : 0,
                "score3" : 0,
                "score4" : 0,
                "users" : ["", "", "", ""]
            }
            await self.sendMsg(game)
        await self.websocket.send("finish" + dumps(msg))
        await self.websocket.close()
        return 0



