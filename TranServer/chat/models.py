from django.db import models
from user.models import User


class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats")
    is_personal = models.BooleanField(default=False)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField()
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)
