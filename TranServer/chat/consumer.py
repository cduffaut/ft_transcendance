from sys import stderr
from .models import Chat, Message
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
import base64
from django.core.files.base import ContentFile


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            if not self.scope["user"].is_authenticated:
                await self.close()
            self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
            await sync_to_async(self.get_user)()
            self.room_group_name = f"chat_{self.chat_id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        except:
            await self.close(1)

    def get_user(self):
        Chat.objects.get(id=self.chat_id).participants.get(
            username=self.scope["user"].username
        )

    async def disconnect(self, close_code=0):
        if close_code == 0:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        await super().disconnect(0)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        text_data_json = json.loads(text_data)
        if "message" in text_data_json:
            message = text_data_json["message"]
            # Save message to database
            await sync_to_async(self.save_message)(message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "user": self.scope["user"].username,
                },
            )
        elif "image" in text_data_json:
            image_data = text_data_json["image"]
            await sync_to_async(self.save_image)(image_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_image",
                    "image": image_data,
                    "user": self.scope["user"].username,
                },
            )

    async def chat_message(self, event):
        message = event["message"]
        username = event["user"]

        await self.send(
            text_data=json.dumps({"username": username, "message": message})
        )

    async def chat_image(self, event):
        image = event["image"]
        username = event["user"]

        await self.send(text_data=json.dumps({"username": username, "image": image}))

    def save_message(self, message_content):
        chat = Chat.objects.get(id=self.chat_id)

        Message.objects.create(
            sender=self.scope["user"],
            chat=chat,
            content=message_content,
            timestamp=timezone.now(),
        )

    def save_image(self, image_data):
        format, imgstr = image_data.split(";base64,")
        ext = format.split("/")[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f"image.{ext}")

        chat = Chat.objects.get(id=self.chat_id)
        Message.objects.create(
            sender=self.scope["user"], chat=chat, image=data, timestamp=timezone.now()
        )
