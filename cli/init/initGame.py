from init.tools import *
from init.DjangoHttpsCommunication import DjangoCommunication
from re import match



class NewGameSettings:
    def __init__(self, djangocom):
        self.gameSettings = None
        termSize = os.get_terminal_size()
        if termSize.columns < 80 or termSize.lines < 20:
            while termSize.columns < 80 or termSize.lines < 20:
                Information("TERMINAL SIZE", "Terminal must be biger than 80 column and 20 lines.", style=STYLERROR)
                termSize = os.get_terminal_size()
        else:
            Information("TERMINAL SIZE", "Terminal must be biger than 80 column and 20 lines.", style=STYLSUCCESS)
        while True:
            value = Question3Value("GAME", "Would you join or create a new game", "join", "create", "Exit")
            if value == 1:
                isok, self.gameSettings = self.joinGame(djangocom)
                if isok and self.gameSettings["nbPlayers"] > 2:
                    Information("ERROR GAME", "Max game 2 players", style=STYLERROR)
                elif isok:
                    break
            elif value == 0:
                isok, dict = self.createNewGame()
                if isok:
                    icode, path = djangocom.createGame(dict)
                    if checkReturnValue(icode):
                        icode, self.gameSettings = djangocom.getGameInfo(path)
                    if checkReturnValue(icode):
                        if self.gameSettings["nbPlayers"] > 2:
                            Information("ERROR GAME", "Max game 2 players", style=STYLERROR)
                        else:
                            Information("GAME", "New game created\nLink : " + djangocom.url + "/game/" + str(self.gameSettings["gameid"]) + "/\nGame id : " + str(self.gameSettings["gameid"]), style=STYLSUCCESS)
                            break
            else:
                doexit(0, "User exit")


    def joinGame(self, djangocom):
        run, value = self.getGameUrl()
        gameData = None
        while run:
            if value:
                icode, gameData = djangocom.getGameInfo(value)
                if checkReturnValue(icode):
                    break
            run, value = self.getGameUrl(style=STYLERROR)
        return run, gameData
            


    def getGameUrl(self, style=STYLE):
        value = inputText("JOIN GAME", "Type game url", style=style)
        if value == None:
            return False, None
        else:
            return True, value


    def createNewGame(self):
        dict = {}
        dict["ballwidth"] = self.getIntSettingRange("NEW GAME", "Ball width (5 - 30) :", 5, 30, 10)
        if dict["ballwidth"] == None:
            return False, None
        dict["planksize"] = self.getIntSettingRange("NEW GAME", "Plank size (10 - 40) :", 10, 40, 20)
        if dict["planksize"] == None:
            return False, None
        dict["Speed"] = self.getFloatSettingRange("NEW GAME", "Speed (0.5 - 3) :", 0.5, 3, 1)
        if dict["Speed"] == None:
            return False, None
        dict["acceleration"] = self.getIntSettingRange("NEW GAME", "Acceleration (0 - 10) :", 0, 10, 0)
        if dict["acceleration"] == None:
            return False, None
        dict["winpoint"] = self.getIntSettingRange("NEW GAME", "Win point (3 - 15) :", 3, 15, 5)
        if dict["winpoint"] == None:
            return False, None
        dict["gamemode"] = MultiChoiceInput("NEW GAME", "Witch mode do you want?", [(0, "offline"), (1, "2 Players"), (3, "IA")])
        if dict["gamemode"] == None:
            return False, None
        return True, dict


    def getIntSettingRange(self, title, text, min, max, default):
        value = inputText(title, text, False, STYLE, str(default))
        if value == None:
            return None
        while value and (not value.isdigit() or float(value) < min or float(value) > max):
            if not value.isdigit():
                value = inputText(title, "Not a number :", False, STYLERROR, str(default))
            else:
                value = inputText(title, ("Input must be between", min, "and", max, ":"), False, STYLERROR, str(default))
        return int(value)

    def getSetting(self, title, text, values):
        listValues = []
        i = 0
        for value in values:
            listValues.append((i, value))
            i += 1
        return radiolist_dialog(
            title=title,
            text=text,
            values=listValues,
            style=STYLE).run

    def getFloatSettingRange(self, title, text, min, max, default):
        floatPattern = r'^\d+(\.\d+)?$'
        value = inputText(title, text, False, STYLE, str(default))
        if value == None:
            return None
        while value and (not match(floatPattern, value) or float(value) < min or float(value) > max):
            if not match(floatPattern, value):
                value = inputText(title, "Not a real number :", False, STYLERROR, str(default))
            else:
                value = inputText(title, ("Input must be between", min, "and", max, ":"), False, STYLERROR, str(default))
        return float(value)

