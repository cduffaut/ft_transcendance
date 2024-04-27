import sys
import os
chemin_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(chemin_parent)
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import radiolist_dialog
from os import system
from color import *

STYLE = Style.from_dict({
    'dialog':             'bg:#101010',
    'dialog frame.label': 'bg:#222222 #ffcc10',
    'dialog.body':        'bg:#252525 #858585',
    'dialog shadow':      'bg:#101010',
})


STYLERROR = Style.from_dict({
    'dialog':             'bg:#101010',
    'dialog frame.label': 'bg:#222222 #ffcc10',
    'dialog.body':        'bg:#252525 #aa0000',
    'dialog shadow':      'bg:#101010',
})
STYLSUCCESS = Style.from_dict({
    'dialog':             'bg:#101010',
    'dialog frame.label': 'bg:#222222 #ffcc10',
    'dialog.body':        'bg:#252525 #00aa00',
    'dialog shadow':      'bg:#101010',
})

def Information(title, text, style=STYLE):
    message_dialog(title=title, text=text, style=style).run()

def Question3Value(title, text, value1, value2, value3, style=STYLE):
    return button_dialog(
        title=title,
        text=text,
        style=style,
        buttons=[
            (value1, 1),
            (value2, 0),
            (value3, -1)
        ]
    ).run()

def Question2Value(title, text, value1, value2):
    return button_dialog(
        title=title,
        text=text,
        style=STYLE,
        buttons=[
            (value1, True),
            (value2, False),
        ]
    ).run()

def inputText(title, text, password=False, style=STYLE, defaultValue=""):
    return input_dialog(
        title=title,
        text=text,
        password=password,
        default=defaultValue,
        style=style).run()

def MultiChoiceInput(title, text, optionValue, style=STYLE):
    return radiolist_dialog(
        title=title,
        text=text,
        values=optionValue,
        style=style
    ).run()



def checkReturnValue(icode):
    if icode >= 500:
        Information("SERVEUR ERROR", "The connection with the serveur fail.")
    elif icode >= 400:
        Information("REQUEST ERROR", "The serveur return an error.")
    else:
        return True
    return False

def doexit(errorCode, errorMsg=""):
    system("clear")
    if errorMsg and errorCode:
        print(RED, errorMsg, RESET)
    elif errorMsg:
        print(GREEN, errorMsg, RESET)
    exit(errorCode)
