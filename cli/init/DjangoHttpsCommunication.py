import sys
import os
chemin_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(chemin_parent)
import requests
from color import *
from time import sleep
from os import system

class DjangoCommunication:
    def __init__(self):
        self.csrfToken = ""
        self.url = None
        self.wsUrl = None
        self.session = requests.Session()
        system("clear")

    def CheckUrl(self, url):
        try:
            response = self.session.get(url + "/register/", verify=False)
        except:
            return 500
        if  response.text.find("<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\"") >= 0:
            self.url = url
            return response.status_code
        return 500

    def setcsrfToken(self, path):
        try:
            response = self.session.get(self.url + path, verify=False)
        except:
            return 500
        system("clear")
        tokenStart = response.text.find("<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\"") + 55
        tokenStop = response.text.find("\">", tokenStart)
        if tokenStart == -1 or tokenStop == -1:
            self.csrfToken = ""
            return 404
        else:
            self.csrfToken = response.text[tokenStart:tokenStop]
            return 200
    
    def createUser(self, user, mail, password):
        value = self.setcsrfToken("/register")
        if value != 200:
            return value
        data = {
        'username': user,
        'email': mail,
        'password': password,
        'csrfmiddlewaretoken': self.csrfToken
        }
        try:
            response = self.session.post(self.url + "/api/signup/", data=data, verify=False)
            return response.status_code
        except:
            return 500
    
    def loginUser(self, user, password):
        value = self.setcsrfToken("/login/")
        if value != 200:
            return value
        data = {
            'username': user,
            'password': password,
            'csrfmiddlewaretoken': self.csrfToken
        }
        try:
            response = self.session.post(self.url + "/api/login/", data=data, verify=False)
        except:
            return 500
        system("clear")
        return response.status_code


    def createGame(self, data):
        from json import loads
        value = self.setcsrfToken("/newGame/")
        data["csrfmiddlewaretoken"] = self.csrfToken
        if value != 200:
            print(RED, "CSRF ERROR", RESET)
            return value, None
        headers = {'Referer': self.url + "/newGame/"}
        try:
            response = self.session.post(self.url + "/newGame/", data=data, verify=False, headers=headers)
        except:
            return response.status_code
        system("clear")
        return response.status_code, loads(response.text)["gameLink"]
    

    def getGameInfo(self, path):
        from json import loads
        try:
            if path.startswith("https://"):
                url = path
            elif path.isdigit():
                url = self.url + "/api/game/" + path
            else:
                url = self.url + path
            response = self.session.get(url, verify=False)
        except:
            return 500
        system("clear")
        if response.status_code >= 400:
            return response.status_code, None
        gameinfo = loads(response.text)["data"]
        return 200, gameinfo