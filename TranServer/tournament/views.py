from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from rest_framework.renderers import JSONRenderer  # Import JSONRenderer
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import sys
from django.shortcuts import redirect
from random import randint
from .models import Tournament
from user.models import User
from game.models import GameUser
from game.serializers import GameSettingsSerializer
from game.consumer import launchGame
from chat.models import Chat, Message
from django.db.models import Count
from random import choice
from .consumer import getUpdate
from django.http import Http404
from asgiref.sync import async_to_sync
from django.utils import timezone
from channels.layers import get_channel_layer

"""Tournament settings management

This function generate all the game instance in database. with information.
after that, the user is added as player inside tournament.
When it s made, the user is redirected to the page for adding user in tournament
"""


def send_message_to_chat_group(chat, message, inviter, user, hostname):
    invite_message = (
        inviter + " has invited you to the tournament: https://" + hostname + message
    )
    print(invite_message, file=sys.stderr)
    Message.objects.create(
        sender=user,
        chat=chat,
        content=invite_message,
        timestamp=timezone.now(),
    )
    channel_layer = get_channel_layer()
    room_group_name = f"chat_{chat.id}"

    # Send message to group
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": "chat_message",
            "message": invite_message,
            "user": user.username,
        },
    )


def get_personal_chat(user):
    return (
        Chat.objects.annotate(participant_count=Count("participants"))
        .filter(is_personal=True, participants=user, participant_count=1)
        .first()
    )


class tournamentSettings(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        return render(request, "html/tournament.html")

    def post(self, request):
        self.data = request.data.copy()
        if not self.checkuser(int(self.data["playerNumber"]), int(self.data["gamesettings"])):
            return Response(
                {"message": "Wrong players number. Or wrong mode."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.tournament = Tournament.objects.create(
            playerNumber=self.data["playerNumber"]
        )
        self.data["tournament"] = self.tournament.id
        if self.data["gamesettings"] == "0":
            self.GenerateMixTree(int(self.data["playerNumber"]))
        elif self.data["gamesettings"] == "2":
            self.generateStandardTree(int(self.data["playerNumber"]), 2)
        else:
            self.generateStandardTree(int(self.data["playerNumber"]), 4)
        if not self.createGamesDb():
            return HttpResponse(
                "Error 500", status=500
            )  # TODO rediriger vers error page
        putUserInGame(self.tournament, request.user)
        if request.data.get("participants") and isinstance(
            request.data.get("participants"), list
        ):
            print("wa have harpts", file=sys.stderr)
            for invite in request.data["participants"]:
                if (
                    invite != request.user.username
                    and User.objects.filter(username=invite).exists()
                ):
                    invite_u = User.objects.get(username=invite)
                    send_message_to_chat_group(
                        get_personal_chat(invite_u),
                        "/tournament/" + str(self.tournament.id),
                        request.user.username,
                        invite_u,
                        request.META.get("HTTP_HOST", ""),
                    )
        return JsonResponse({"id": str(self.tournament.id)}, status=200)
        # return render(request, 'addUser.html', {'id': self.tournament.id})

    def checkuser(self, playernumber, mode):
        listeMode = [0, 2, 4]
        liste2p = [4, 8, 16]
        liste4p = [8, 16]
        listmix = [4, 6, 8, 10, 12, 14, 16]
        if mode not in listeMode:
            return False
        if playernumber > 16 or playernumber % 2:
            return False
        if mode == 2 and playernumber in liste2p:
            return True
        if mode == 0 and playernumber in listmix:
            return True
        return playernumber in liste4p

    def getMixLevel(self, player):
        game2p = 0
        game4p = 0
        while player >= 6:
            player -= 6
            game2p += 1
            game4p += 1
        while player >= 4:
            player -= 4
            game4p += 1
        while player >= 2:
            player -= 2
            game2p += 1
        if (game4p + game2p) % 2 and game4p:
            game4p -= 1
            game2p += 2
        elif (game4p + game2p) % 2:
            game2p -= 2
            game4p += 1
        liste = []
        while game4p and game2p:
            if randint(1, 2) % 2:
                liste.append(4)
                game4p -= 1
            else:
                liste.append(2)
                game2p -= 1
        while game4p:
            liste.append(4)
            game4p -= 1
        while game2p:
            liste.append(2)
            game2p -= 1
        return liste

    def GenerateMixTree(self, player: int):
        self.MatchListe = []
        while player >= 6:
            listeMatchLevel = self.getMixLevel(player)
            player = len(listeMatchLevel)
            self.MatchListe.append(listeMatchLevel)
        if player == 4:
            liste = [4]
        else:
            liste = [2]
        self.MatchListe.append(liste)

    def generateStandardTree(self, player: int, gameplayer: int):
        self.MatchListe = []
        while player >= gameplayer:
            player = player // gameplayer
            self.MatchListe.append([gameplayer] * player)

        # game = Game.objects.create(tournament=tournament)

    def createGamesDb(self):
        i = len(self.MatchListe) - 1
        firstGameDb = True
        oldListe = None
        for level in reversed(self.MatchListe):
            j = 0
            liste = []
            for gamePlayer in level:  # iterate game in level. value 2 or 4
                nextGameId = 0
                if oldListe:
                    for element in oldListe:
                        if element[0]:
                            nextGameId = element[1]
                            element[0] -= 1
                            break
                id = self.putGamesDb(i, j, gamePlayer, nextGameId, firstGameDb)
                firstGameDb = False
                if not id:
                    return False
                liste.append([gamePlayer, id])
                j += 1
            oldListe = liste.copy()
            i -= 1
        return True

    def putGamesDb(self, level, levelPos, gameMode, nextGameId, firstGameGenerated):
        if gameMode == 2:
            self.data["gamemode"] = 1
        else:
            self.data["gamemode"] = 2
        self.data["gameLevel"] = level
        self.data["levelPos"] = levelPos
        if nextGameId:
            self.data["nextGame"] = nextGameId
        if firstGameGenerated:
            self.data = self.changeData(self.data)
        serializer = GameSettingsSerializer(data=self.data)
        if serializer.is_valid():
            return serializer.save().id
        else:
            print("ERROR DB : ", serializer.errors, file=sys.stderr)
            return None

    def changeData(self, data):
        if (
            data.get("ballwidth")
            and data.get("planksize")
            and data.get("Speed")
            and data.get("acceleration")
        ):
            data["ballwidth"] = int(data["ballwidth"]) / 100
            data["planksize"] = int(data["planksize"]) / 100
            data["Speed"] = float(data["Speed"]) / 10
            if int(data["acceleration"]):
                data["acceleration"] = int(data["acceleration"]) / 100

            return data
        return None


# def TournamentAddUser(request, id):
#     return render(request, 'addUser.html')

""" Tournament view
When a user join a tournament view:
if the user is in the tournament, and as to play, he is automatically redirected to the game page.
In other case, if the user is not added, he is added to the tournament.

When the last player join, the game instance is launch. and an update is send.
"""


class TournamentView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        self.id = id
        if not Tournament.objects.filter(pk=id).exists():
            raise Http404("Tournament does not exist")
        self.tournament = Tournament.objects.get(pk=self.id)
        self.request = request
        tournamentSize = self.getGameByLevel()
        return render(
            request,
            "html/bracket.html",
            {"tournamentSize": tournamentSize, "username": request.user.username},
        )

    def getGameByLevel(self):
        i = 0
        gameliste = []
        value = 1
        while value:
            value = self.tournament.game_set.filter(gameLevel=i).count()
            if value:
                gameliste.append(value)
            i += 1
        return gameliste

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            raise exc
        return super().handle_exception(exc)


class TournamentJoin(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        self.id = id
        if not Tournament.objects.filter(pk=id).exists():
            raise Http404("Tournament does not exist")
        self.tournament = Tournament.objects.get(pk=self.id)
        self.request = request
        tournamentSize = self.getGameByLevel()
        return render(
            request,
            "html/bracket.html",
            {"tournamentSize": tournamentSize, "username": request.user.username},
        )

    def getGameByLevel(self):
        i = 0
        gameliste = []
        value = 1
        while value:
            value = self.tournament.game_set.filter(gameLevel=i).count()
            if value:
                gameliste.append(value)
            i += 1
        return gameliste

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            raise exc
        return super().handle_exception(exc)


class TournamentJoin(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        self.id = id
        if not Tournament.objects.filter(pk=id).exists():
            raise Http404("Tournament does not exist")
        self.request = request
        id = self.newUserConnection()

    # if user as to play: return gameid
    def newUserConnection(self):
        self.tournament = Tournament.objects.get(pk=self.id)
        user_ids = self.tournament.game_set.all().values_list(
            "gameuser__user", flat=True
        )
        usernames = User.objects.filter(id__in=user_ids).values_list(
            "username", flat=True
        )
        if (
            not str(self.request.user) in usernames
            and user_ids.count() <= self.tournament.playerNumber
        ):
            if putUserInGame(self.tournament, self.request.user):
                launchTournament(self.tournament)
        return 0

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            raise exc
        return super().handle_exception(exc)


def putUserInGame(tournament, user):
    games = tournament.game_set.filter(gameLevel=0)
    availablGame = []
    availablPlace = 0
    for game in games:
        if game.gamemode == 1 and game.gameuser_set.count() < 2:
            availablGame.append(game)
            availablPlace += 2 - game.gameuser_set.count()
        elif game.gamemode == 2 and game.gameuser_set.count() < 4:
            availablGame.append(game)
            availablPlace += 4 - game.gameuser_set.count()
    if availablGame:
        game = choice(availablGame)
        user = GameUser.objects.create(user=user, game=game)
        game.gameuser_set.add(user)
        tournament.playerNumber = int(tournament.playerNumber) + 1
    if availablPlace == 1:
        return True
    return False


def launchTournament(tournament):
    games = tournament.game_set.filter(gameLevel=0)
    for game in games:
        launchGame(game)
    async_to_sync(getUpdate)(tournament.id)
