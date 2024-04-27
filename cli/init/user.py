from re import match
from init.tools import *
from init.DjangoHttpsCommunication import DjangoCommunication


class User:
    def __init__(self, Django):
        self.username = ""
        self.userToken = None
        self.Django = Django
        var = False
        while not var:
            value = Question3Value("MAIN", "Login or signup?", "LOGIN", "signup", "Exit")
            if value == 1:
                var = self.doLogin()
            elif value == 0:
                var = self.doRegistration()
            else:
                doexit(0, "User exit")
        
    def doLogin(self):
        user, pwd = self.login()
        if pwd == None:
            return False
        value = self.Django.loginUser(user, pwd)
        while value >= 400 and value != 500:
            result = Question3Value("LOGIN", "Login fail.", "Retry", "signup", "exit", style=STYLERROR)
            if result == 1:
                user, pwd = self.login(error=True)
                value = self.Django.loginUser(user, pwd)
            elif result == 0:
                self.doRegistration()
                return
            else:
                doexit(1, "User exit.")
        if value == 500:
                doexit(1, "Error: Serveur not accessible.")
        Information("LOGIN", "User connection success.", style=STYLSUCCESS)
        return True
        

    def login(self, error=False):
        if error:
            user = inputText("LOGIN", "Wrong login. User : ", False, STYLERROR)
            if user == None:
                return None, None
            pwd = inputText("LOGIN", "Wrong login. password : ", True, STYLERROR)
        else:
            user = inputText("LOGIN", "Please type your username: ")
            if user == None:
                return None, None
            pwd = inputText("LOGIN", "Please type your password: ", password=True)
        return user, pwd

    def doRegistration(self):
        user, mail, pwd = self.registration()
        if pwd == None:
            return False
        value = self.Django.createUser(user, mail, pwd)
        while value >=400 and value != 500:
            result = Question3Value("ERROR" + str(value), "User or email already exists or email is invalid.", "signup", "login", "exit", style=STYLERROR)
            if result == 0:
                self.doLogin()
                return
            elif result == -1:
                doexit(1)
            user, mail, pwd = self.registration()
            value = self.Django.createUser(user, mail, pwd)
        if value == 500:
                doexit(1, "Error: Serveur not accessible.")
        Information("SIGNUP", "User creation success.\nPlease validate your email before proceeding.", style=STYLSUCCESS)
        doexit(0, "Exit due to email validation required.")
        return True

    def registration(self):

        user = inputText("REGISTRATION", "Username :", defaultValue="a")
        if user == None:
            return None, None, None
        while not user:
            user = inputText("REGISTRATION", "Username :", style=STYLERROR)
        mail = self.getMail()
        if mail == None:
            return None, None, None
        pwd = self.getPwd()
        return user, mail, pwd


    def getMail(self, error=False):
        mailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        inputmsg = "E-mail :"
        mail = inputText("REGISTRATION", inputmsg, defaultValue="a@a.aa")
        while mail and not match(mailPattern, mail):
            inputmsg = "Wrong mail, Try again :"
            mail = inputText("SIGNUP", inputmsg, False, STYLERROR)
        return mail

    def getPwd(self):
        text1 = "Type password :"
        text2 = "Confirm password :"
        pwd1 = inputText("SIGNUP", text1, True, defaultValue="a")
        if pwd1 == None:
            return None
        pwd2 = inputText("SIGNUP", text2, True, defaultValue="a")
        if pwd2 == None:
            return None
        while not pwd1 or pwd1 != pwd2:
            if not pwd1:
                text1 = "No password write :"
            else:
                text1 = "Password not corresponding :"
            pwd1 = inputText("SIGNUP", text1, True, STYLERROR)
            if pwd1 == None:
                return None
            pwd2 = inputText("SIGNUP", text2, True, STYLERROR)
            if pwd2 == None:
                return None
        return pwd1
