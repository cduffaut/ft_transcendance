import asyncio
import websockets
import os
from sys import stderr
from wsServer import WebSocketServer
from time import sleep
from json import loads

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
ORANGE = "\033[38;2;255;165;0m"

class DjangoCli:
    def __init__(self, wsServer, DjangoUrl):
        self.websocket = None
        self.DjangoUrl = DjangoUrl
        self.wsServer = wsServer

    def print(self, msg):
        print(MAGENTA, "Django client game :", msg, RESET, file=stderr)

    async def connectDjango(self):
        i = 0
        sleep(4)
        while i <= 10: 
            try:
                self.websocket = await websockets.connect(self.DjangoUrl)
                self.print(GREEN + "GameServ, connected to Daphne.")
                # await self.websocket.send("connected")
                break
            except:
                self.print(ORANGE + "Server daphne not available.")
                sleep(1)
                i += 1
        if i > 10:
            self.print(RED + "Client fail 10x the connection with daphne ws." + self.DjangoUrl)
            self.print(RED + "Closing Django game server client")
            exit(1)

        # Coroutine asynchrone pour lire les messages de manière non bloquante
    async def receive_messages(self):
        i = 0
        while True:
            try:
                message = await self.websocket.recv()
                print(message, file=stderr)
                gameid = loads(message)["message"]["gameid"]
                if not gameid in self.wsServer.clients[1]:
                    os.environ['newGame'] = message
                    os.system("python3 game/game.py &")
                else:
                    print(ORANGE, "GAME ALREADY EXISTING", RESET, file=stderr)
            except websockets.exceptions.ConnectionClosed:
                i += 1
                self.print(ORANGE + "Connection to server django closed")
                if i == 5:
                    break
                else:
                    await self.connectDjango()

    async def sendDjangoMsg(self):
        while True:
            messages = self.wsServer.getDjangoMsg()
            if messages:
                for msg in messages:
                    await self.websocket.send(msg)
            await asyncio.sleep(0.1)


    async def close_connection(self):
        if self.websocket and self.websocket.open:
            await self.websocket.close()
