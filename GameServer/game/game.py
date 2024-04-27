import os
from wsClient import WebSocketClient
from gameLogic import gameLogic
import json
import asyncio
from sys import stderr
from time import sleep, time
from random import choice

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
ORANGE = "\033[38;2;255;165;0m"

# Convertir JSON en dictionnaire
# gameSettings = loads(os.environ.get("newGame"))

#dictionary communication bitween serveur and client.
GAME = {
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
	"score4" : 0
}

gameSettings = {
    "ballwidth" : 0.03, #max size plank size calculation
    "planksize" : 0.3, #max size 50%
    "Speed" : 0.002,
    "acceleration" : 0.01, #increase speed each bounce
    "playeramount" : 2,
    "winpoint" : 10,
    "user1" : "",
    "user2" : "",
    "user3" : "",
    "user4" : "",
    "gameid" : 0,
}

gameEndDjango = {
    "user1" : ("", 3),
    "user2" : ("", 4),
    "user3" : ("", 5),
    "user4" : ("", 2),
    "gameid" : 0
    }


def listUser(data):
    liste = []
    for cle, value in data.items():
        if cle.startswith("user"):
            if value:
                liste.append(value)
    return liste


async def WaitUntilPlayers(ws, data):
    lockedPlayers = listUser(data) #list user locked
    logedPlayers = []
    startTime = time()
    while len(logedPlayers) < data["playeramount"] and time() - startTime < 120:
        msgs = ws.getMsg()
        if msgs:
            for msg in msgs:
                if msg.endswith("login"):
                    logedPlayers = await addPlayers(msg[:-5], lockedPlayers, logedPlayers, data["playeramount"])
                elif msg.endswith("logout"):
                    logedPlayers = await removePlayer(msg[:-6], logedPlayers)
        await asyncio.sleep(0.5)
    if len(logedPlayers) == data["playeramount"]:
        await ws.sendUserJoin(logedPlayers)
    else:
        await playerInGame(logedPlayers, ws, data)
        return None
    return logedPlayers

async def removePlayer(rmPlayer, logedPlayers):
    if rmPlayer in logedPlayers:
        logedPlayers.remove(rmPlayer)
    return logedPlayers

async def addPlayers(newUser, lockedPlayers, logedPlayers, playeramount):
    if newUser in lockedPlayers and newUser not in logedPlayers:
        logedPlayers.append(newUser)
    elif newUser not in logedPlayers:
        logedPlayersLen = len(lockedPlayers)
        for players in logedPlayers:
            if players not in lockedPlayers:
                logedPlayersLen += 1
        if logedPlayersLen < playeramount:
            logedPlayers.append(newUser)
    return logedPlayers


async def playerInGame(logedPlayers, wsCli, data):
    dico = {}
    dico["gameid"] = data["gameid"]
    lockedPlayers = listUser(data)
    if len(logedPlayers):
        winner = choice(logedPlayers)
        dico["user1"] = [winner, 1]
    elif len(lockedPlayers):
        winner = choice(lockedPlayers)
        dico["user1"] = [winner, 1]
    await wsCli.sendMsg(GAME)
    await wsCli.sendEndGame(dico, gameError=True)
    



def updateUser(userliste, data):
    if data["gamemode"] == 0:
        return ["Player1", "Player2"]
    elif data["gamemode"] == 3:
        userliste.append("IA")
    return userliste


def putDatagameSettings(data, settings):
    elem = ["ballwidth", "planksize", "Speed", "acceleration", "playeramount", "winpoint", "user1", "user2", "user3", "user4", "gameid"]
    if not data.get("gameid"):
        print("\033[31mGameid not available.\033[0m", file=stderr)
        exit(1)
    for i in elem:
        if data.get(i):
            settings[i] = data[i]
    return settings


async def main():
    gameSettings = {
        "ballwidth" : 0.03, #max size plank size calculation
        "planksize" : 0.3, #max size 50%
        "Speed" : 0.5,
        "acceleration" : 0.05, #increase speed each bounce
        "playeramount" : 2,
        "winpoint" : 10,
        "user1" : "",
        "user2" : "",
        "user3" : "",
        "user4" : "",
        "gameid" : 0,
    }

    game = {
        "ballx" : 0, # -0.5 -> 0.5
        "bally" : 0, # -0.5 -> 0.5
        "p1" : 0, # -0.5 -> 0.5
        "p2" : 0, # -0.5 -> 0.5
        "p3" : 0, # -0.5 -> 0.5
        "p4" : 0, # -0.5 -> 0.5
        "state" : "playing",
        "score1" : 0,
        "score2" : 0,
        "score3" : 0,
        "score4" : 0
    }

    DjangoData = json.loads(os.environ.get("newGame"))["message"]
    print(RED, "|[---Creating game instance", DjangoData["gameid"], "...---]|", RESET)
    gameSettings = putDatagameSettings(DjangoData, gameSettings)
    wsServ = "ws://localhost:8001/game/" + str(gameSettings["gameid"])

    client = WebSocketClient(wsServ)
    await client.connect()
    asyncio.create_task(client.receive_messages())
    

    userliste = await WaitUntilPlayers(client, DjangoData)
    if userliste == None:
        print(MAGENTA, "Game end for missing players", RESET, file=stderr)
        exit(0)
    userliste = updateUser(userliste, DjangoData)

    print("|[---Userlist---]|", userliste)
    print("|[--Launching game logic instance--]|")
    game_logic_instance = gameLogic(client, gameSettings, game, userliste)
    await game_logic_instance.start_game()  # Assurez-vous que la méthode start est bien définie pour démarrer BottiBotto et toute autre initialisation asynchrone

    print("|[---Game instance created---]|")

if __name__ == "__main__":
    asyncio.run(main())