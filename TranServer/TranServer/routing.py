from django.urls import re_path, path
from chat.consumer import ChatConsumer
from game.consumer import GameServerConsumer
from tournament.consumer import TournamentConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:chat_id>/', ChatConsumer.as_asgi()),
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
    path('ws/tournament/<int:tournament_id>/', TournamentConsumer.as_asgi()),
    re_path(r'wsgameserver/$', GameServerConsumer.as_asgi())
]