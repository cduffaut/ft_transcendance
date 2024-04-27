import sys
import os
from color import *
from init.initGame import NewGameSettings
from init.user import User
from init.DjangoHttpsCommunication import DjangoCommunication
from init.tools import *
from game.DataTransmission import DataTransmission
from game.gameGui import GameGui2p
from ascii import Ascii
from time import sleep
import asyncio


def getUrl(Django):
    url = inputText("TRANSCENDANCE", "Write the server url.", defaultValue="https://127.0.0.1")
    if url == None:
        doexit(0, "User exit")
    while not checkUrlInput(url, Django):
        url = inputText("TRANSCENDANCE", "Invalide url. Try again!", style=STYLERROR)
        

def checkUrlInput(url, Django):
    if not url.startswith("https://"):
        return False
    urlSplited = url.split("/")
    if len(url) < 3:
        return False
    url = urlSplited[0] + "//" + urlSplited[2]
    return Django.CheckUrl(url) == 200



def InitCli():
    asciiData = Ascii()
    os.system("clear")
    Django = DjangoCommunication()
    # asciiData.putString("TRANSCENDENCE",GREEN, RESET)
    # asciiData.putString("    Cecile et David",BLUE, RESET)
    # asciiData.putString("Alexandre et Paul",BLUE, RESET)
    # sleep(4)
    # Information("TRANSCENDANCE", "Welcome to the transcendance CLI")
    getUrl(Django)
    User(Django)
    return Django, asciiData

def asWin(message, username):
    if message:
        if message["score1"] > message["score2"]:
            return message["users"][0]
        else :
            return message["users"][1]



async def runGame(dataTransmission, gameGui):
    wsKey = asyncio.create_task(dataTransmission.ConnectWsKeyBinding())
    messages_task = asyncio.create_task(dataTransmission.receive_messages())
    game_update_task = asyncio.create_task(gameGui.updateGame())
    return await asyncio.gather(wsKey, messages_task, game_update_task)


if __name__ == "__main__":
    djangocom, asciidata = InitCli()
    while True:
        gameSettings = NewGameSettings(djangocom).gameSettings
        if not gameSettings:
            Information("UNKNOW ERROR", "Unknow Error! Retry!", style=STYLERROR)
        else:
            dataTransmission = DataTransmission(gameSettings, djangocom.url)
            gameGui = GameGui2p(gameSettings, dataTransmission, asciidata)
            results = asyncio.run(runGame(dataTransmission, gameGui))
            if str(results[0]).isdigit():
                os.system("clear")
                Information("ERROR" + str(results[0]), "Is the game ready to play?", style=STYLERROR)
            else:
                Information("END GAME", str(asWin(results[2], gameSettings["user"])) + " wins this game.")
