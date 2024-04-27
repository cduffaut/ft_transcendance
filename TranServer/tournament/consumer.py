from channels.layers import get_channel_layer
import json
from tournament.models import Tournament
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import Count

""" Tournament ws manager
When a user join a brodcast of actual state of tournament is send to each player
it s made by the function getUpdate
"""


class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope.get("user").is_authenticated:
            await self.close()
        self.tournamentId = self.scope["url_route"]["kwargs"]["tournament_id"]
        self.room_group_name = f"tournament_{self.tournamentId}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        data = await getUpdate(self.tournamentId)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_update",
                "data": data,
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_update(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

@sync_to_async
def getUpdate(id):
    tournament = Tournament.objects.get(pk=id)
    data = []
    games = tournament.game_set.all()
    gamesUser = tournament.game_set.filter(gameLevel=0).aggregate(total_users=Count("gameuser"))["total_users"]
    dico = {}
    dico["tournamentFull"] = gamesUser == tournament.playerNumber
    for game in games:
        data.append(putGameInDict(game))
    dico["games"] = data
    return dico



def putGameInDict(game):
    dico = {}
    gameusers = game.gameuser_set.all()
    i = 0
    dico["gameId"] = game.id
    for gameuser in gameusers:
        dico["player{}Id".format(i)] = gameuser.user.username
        dico["score{}".format(i)] = gameuser.points
        i += 1
    dico["isRunning"] = game.gameRunning
    dico["level"] = game.gameLevel
    dico["pos"] = game.levelPos + 1
    return dico
