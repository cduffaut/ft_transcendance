import json
from channels.generic.websocket import AsyncWebsocketConsumer
from tournament.consumer import getUpdate
from .models import Game, GameUser
from user.models import User
from chat.models import Message, Chat
from tournament.consumer import TournamentConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from django.middleware.csrf import get_token
from sys import stderr
from django.utils import timezone
from django.db.models import Count


"""Game ws manager
Manage the connection between game server and django.
Send tournament update in case of tournament game end.
Also set the winer as next game player
"""


class GameServerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.path = self.scope["path"]
        self.group_name = "gameServer"
        self.channel_layer = get_channel_layer()

        # Ajoute le consommateur WebSocket au groupe
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Implement any necessary cleanup logic here
        await self.channel_layer.group_discard("gameServer", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Here you should handle incoming messages, but for now, let's just send a response back
        data = json.loads(text_data)
        game_id = data["gameid"]
        game = await sync_to_async(Game.objects.get)(id=game_id)
        winner = await self.putGameResultDb(game, data)
        await self.tournamentEndGame(game, winner)

    async def game_msg(self, event):
        message = event["message"]  # Accéder au message dans l'événement
        await self.send(text_data=json.dumps({"message": message}))

    @sync_to_async
    def tournamentEndGame(self, game, winner):
        if game.tournament:
            tournamentId = game.tournament.id
            if winner and game.nextGame:
                nextGame = game.nextGame
                GameUser.objects.create(user=winner.user, game=nextGame)
                if nextGame.gameuser_set.count() > 0 and nextGame.gameuser_set.count() < 3:
                    launchGame(nextGame)
            if tournamentId:
                async_to_sync(self.sendUpdateTournamentview)(tournamentId)
    @sync_to_async
    def putGameResultDb(self, game, data):  # return winner
        game.gameRunning = False
        if game.gamemode > 0 and game.gamemode < 3:
            maxPoint = 0
            winner = None
            for cle, value in data.items():
                if cle.startswith("user") and value[1] > maxPoint:
                    maxPoint = value[1]
            for cle, value in data.items():
                if cle.startswith("user") and value[0]:
                    user = User.objects.get(username=value[0])
                    if GameUser.objects.filter(user=user).exists():
                        gameuser = GameUser.objects.filter(user=user, game=game).first()
                        gameuser.points = value[1]
                        gameuser.save()
                    else:
                        GameUser.objects.create(
                            user=user, game=game, points=value[1]
                        )
                    if maxPoint > 1:
                        user.total_games += 1
                        if value[1] == maxPoint:
                            user.wins += 1
                        user.save()
                    if value[1] == maxPoint:
                        winner = gameuser

            game.save()
            return winner
        gameuser = game.gameuser_set.first()
        gameuser.points = 1
        gameuser.save()
        game.save()
        return None

    async def sendUpdateTournamentview(self, tournamentId):
        data = await getUpdate(tournamentId)
        await self.channel_layer.group_send(
            "tournament_" + str(tournamentId),
            {
                "type": "send_update",
                "data": data,
            },
        )

    async def send_data(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))


def get_personal_chat(user):
    return (
        Chat.objects.annotate(participant_count=Count("participants"))
        .filter(is_personal=True, participants=user, participant_count=1)
        .first()
    )


"""Launch game instance
This class take the information and send for launching a game instance.
"""


class launchGame:
    def __init__(self, game, host="", inviter=""):
        self.chanelLayer = get_channel_layer()
        data = self.generateGame(game, self.generateDico(game))
        self.sendData(data)
        self.host = host
        self.inviter = inviter
        self.id = game.id
        game.gameRunning = True
        game.save()
        for game_user in game.gameuser_set.all():
            self.send_message_to_chat_group(game_user.user)

    def generateDico(self, game):
        dico = {}
        dico["gameid"] = game.id
        dico["ballwidth"] = game.ballwidth
        dico["planksize"] = game.planksize
        dico["Speed"] = game.Speed
        dico["winpoint"] = game.winpoint
        dico["gamemode"] = game.gamemode
        if game.tournament:
            dico["tournamentid"] = game.tournament.id
        else:
            dico["tournamentid"] = 0
        return dico

    def generateGame(self, game, dico):
        if game.gamemode == 1:  # 2p offline, 2p online
            dico["playeramount"] = 2
        elif game.gamemode == 2:  # 4p
            dico["playeramount"] = 4
        else:  # game.gamemode = 3 = IA
            dico["playeramount"] = 1
        users = game.gameuser_set.all().values_list("user__username", flat=True)
        i = 0
        for user in users:
            dico["user{}".format(i)] = user
            i += 1
        return dico

    def sendData(self, data):
        async_to_sync(self.chanelLayer.group_send)(
            "gameServer",
            {
                "type": "game_msg",
                "message": data,
            },
        )

    def send_message_to_chat_group(self, user):
        invite_message = (
            self.inviter
            + " has invited you to the game: https://"
            + self.host
            + "/game/"
            + str(self.id)
        )

        chat = get_personal_chat(user)

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
