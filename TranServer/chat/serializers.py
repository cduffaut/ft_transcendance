from rest_framework import serializers
from .models import Chat, Message
from user.serializers import UserSerializer_Username
import base64
import imghdr


class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer_Username(many=True)

    class Meta:
        model = Chat
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.username")
    chat = serializers.ReadOnlyField(source="chat.id")
    image = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("id", "sender", "chat", "content", "timestamp", "image")

    def get_image(self, obj):
        if obj.image:
            with open(obj.image.path, "rb") as f:
                image_data = f.read()
                file_format = imghdr.what(None, h=image_data)
                encoded_image = base64.b64encode(image_data).decode("utf-8")
                if file_format:
                    image_data_string = (
                        f"data:image/{file_format};base64,{encoded_image}"
                    )
                    return image_data_string
                else:
                    return None
        else:
            return None
