from sys import stderr
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer  # Import JSONRenderer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from rest_framework.permissions import IsAuthenticated


class ChatListView(APIView):
    """Contains the endpoint for getting all of a users' chats,\n
    or getting/creating/deleting a specific chat

    Methods:
        GET (All, One)\n
        POST (One)\n
        DELETE (One)
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request, chat_id=None):
        """For a user that is logged in return json containg the chats' id and participants

        Args:
            route (get all chats): /api/chat
            route (one): /api/chat/{chat_id}

        Returns:
            [multiple]
            id: the chat id
            participants: the chat's participants' usernames
        """

        if chat_id is not None:
            try:
                chat = Chat.objects.get(pk=chat_id)
                if not chat.participants.contains(request.user):
                    return JsonResponse(
                        {"error": "Insufficient permissions: Access Denied"}, status=401
                    )
                serializer = ChatSerializer(chat)
                return Response(serializer.data)
            except Chat.DoesNotExist:
                return JsonResponse({"error": "Chat not found"}, status=404)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=403)
        try:
            serializer = ChatSerializer(request.user.chats.all(), many=True)
        except Exception as e:
            return JsonResponse(
                {"error": "Insufficient permissions: Access Denied"}, status=401
            )
        return Response(serializer.data)

    def post(self, request, chat_id=None):
        """Create a new chat for a user that is logged in

        Args:
           route: /api/chat
        """
        try:
            chat_data = request.data
            print(chat_data, file=stderr)
            if not chat_data:
                return Response(
                    "Request data is empty ", status=status.HTTP_400_BAD_REQUEST
                )

            participants = chat_data["participants"]
            if not participants or not isinstance(participants, list):
                return Response(
                    "Participants list is missing or invalid",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            chat = Chat.objects.create()
            if request.user.username not in participants:
                participants.append(request.user.username)

            for username in participants:
                user_exists = User.objects.filter(username=username).exists()
                if user_exists:
                    user = User.objects.get(username=username)
                    chat.participants.add(user)
                else:
                    # Handle case where user does not exist
                    return Response(
                        f"User '{username}' does not exist",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            chat.save()
            return Response("", status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(
                "'participants' key is missing in request data",
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, chat_id=None):
        """Deletes the current user from the chat.\n
        If the chat is empty after the operation, the chat is deleted

        Args:
            route: /api/chat/{chat_id}
        """
        if chat_id is None:
            return JsonResponse({"error": "Invalid chat ID"}, status=400)
        try:
            chat = Chat.objects.get(pk=chat_id)
            participant = get_object_or_404(chat.participants, id=request.user.id)
            chat.participants.remove(participant)
            chat.save()
            if chat.participants.count == 0:
                chat.delete()
                return JsonResponse(
                    {"message": "Chat deleted successfully"}, status=200
                )
            return JsonResponse(
                {"message": "Participant removed from chat"}, status=200
            )
        except Chat.DoesNotExist:
            return JsonResponse({"error": "Chat does not exist"}, status=401)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@login_required
def general_chat(request):
    return render(request, "html/generalchat.html")


@login_required
def chat_view(request):
    return render(request, "chat_page.html")


def ws_view(request):
    return render(request, "test.html")


class MessageListView(APIView):
    """API endpoint for messages

    Args:
        route: /api/messages/{chat_id}

    Methods:
        GET

    Returns (example):
        [
            {
                "id": 1,
                "sender": "asdf",
                "content": "asdfasdfasdf",
                "timestamp": "2024-03-15T09:02:36.985614Z",
                "chat": 1
            },
            ...
        ]
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(pk=chat_id)
            if not chat.participants.contains(request.user):
                return JsonResponse(
                    {"error": "Insufficient permissions: Access Denied"}, status=401
                )
            serializer = MessageSerializer(Message.objects.filter(chat=chat), many=True)
            return Response(serializer.data)
        except Chat.DoesNotExist:
            return JsonResponse({"error": "Chat not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=403)
