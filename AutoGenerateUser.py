import requests
from os import system
import sys

class AutoGenerateUser:
    def __init__(self, username, url="https://127.0.0.1"):
        self.csrfToken = ""
        self.url = url
        self.session = requests.Session()
        mail = username + "@42.ch"

        value = self.createUser(username, mail, username)
        if value >= 400:
            print("ERROR :", value)
            exit(0)

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
    

if __name__ == "__main__":
    # Itère à travers les arguments
    for arg in sys.argv[1:]:
        AutoGenerateUser(arg)
    print("USER CREATED")