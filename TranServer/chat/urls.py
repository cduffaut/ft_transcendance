from django.urls import path
from .views import ChatListView, chat_view, MessageListView, ws_view
from .consumer import ChatConsumer
from .views import general_chat

urlpatterns = [
    path("chats/", chat_view, name="chats"),
    path("api/chat/", ChatListView.as_view(), name="chat_api"),
    path("api/chat/<str:chat_id>/", ChatListView.as_view(), name="chat_api"),
    path(
        "api/messages/<str:chat_id>/",
        MessageListView.as_view(),
        name="chat_message_view",
    ),
    path("test/", ws_view, name="ws_view"),
    path("generalchat/", general_chat, name="general_chat"),
]
