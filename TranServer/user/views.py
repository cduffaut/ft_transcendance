from sys import stderr
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, JsonResponse, Http404
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    password_validation,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User
from game.models import Game, GameUser
from chat.models import Chat
from .serializers import (
    UserSerializer,
    UserSerializer_Username,
    PersonalUserSerializer,
    OtherUserSerializer,
    ColorsUserSerializer,
    ColorUpdateSerializer,
)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import smtplib
import os
from datetime import timedelta

MAIL = False


@api_view(["POST"])
@renderer_classes([JSONRenderer])
def api_signup(request):
    try:
        serializer = UserSerializer(data=request.data)
        password = request.data.get("password")
        try:
            password_validation.validate_password(password)
        except ValidationError as e:
            return JsonResponse(
                {"error": e.messages}, status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            user = serializer.save()
            if not MAIL:
                chat = Chat.objects.create()
                chat.participants.add(user)
                chat.is_personal = True
                chat.save()
                user.mailValidate = True
                user.save()
                login(request, user)
                return Response(
                    {"message": "You have been logged in"},
                    status=status.HTTP_200_OK,
                )
            elif sendMail(user, user.email, isMail=True):
                chat = Chat.objects.create()
                chat.participants.add(user)
                chat.is_personal = True
                chat.save()
                return render(request, "html/email_sent.html")
            else:
                user.delete()
                return Response(
                    {"message": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@renderer_classes([JSONRenderer])
@login_required
def api_pending_invite(request):
    try:
        invites = request.user.sent_invites.all()
        return Response(
            UserSerializer_Username(invites, many=True).data,
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FriendListView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request, username=None):
        try:
            friends = request.user.friends.all()
            return Response(
                UserSerializer_Username(friends, many=True).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, username=None):
        try:
            friend = request.user.invites.filter(username=username)
            if friend:
                request.user.friends.add(friend.first())
                request.user.invites.remove(friend.first())
                return JsonResponse(
                    {"message": "accepted friend invite"}, status=status.HTTP_200_OK
                )
            return JsonResponse(
                {"error": "no invite found"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username=None):
        if not username:
            return Response(
                "Please provide a username", status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(username=username)
            if user.friends.filter(username=request.user.username):
                user.friends.remove(request.user)
                return Response("Removed user", status=status.HTTP_200_OK)
            return Response("User is not friend", status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                "User with provided username does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@renderer_classes([JSONRenderer])
@login_required
def undo_invite_api(request, username):
    try:
        user = User.objects.get(username=username)
        user.invites.remove(request.user)
        return Response("Rescinded invited", status=status.HTTP_200_OK)
    except Exception as e:
        return Response("Invalid request", status=status.HTTP_400_BAD_REQUEST)


@renderer_classes([JSONRenderer])
@login_required
@api_view(["GET"])
def is_blocked_api(request, username):
    try:
        user = User.objects.get(username=username)
        if user.blocked.filter(username=request.user.username):
            return Response(True, status=status.HTTP_200_OK)
        return Response(False, status=status.HTTP_200_OK)
    except Exception as e:
        return Response("Invalid request", status=status.HTTP_400_BAD_REQUEST)


class InviteListView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]
    """
    Get your invites
    """

    def get(self, request, username=None):
        try:
            invites = request.user.invites.all()
            return Response(
                UserSerializer_Username(invites, many=True).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    """
    Send invites to someone
    """

    def post(self, request, username=None):
        if not username:
            return Response(
                "Please provide a username", status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(username=username)
            if request.user.blocked.filter(username=username):
                return Response(
                    "You can't invite a user that you've blocked",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.blocked.filter(username=request.user.username):
                return Response(
                    "You can't invite a user that has blocked you",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.invites.filter(username=username):
                return Response(
                    "Invite already exists", status=status.HTTP_400_BAD_REQUEST
                )
            if request.user == user:
                return Response(
                    "You cannot invite yourself", status=status.HTTP_400_BAD_REQUEST
                )
            if request.user.invites.filter(username=username):
                request.user.invites.remove(user)
                request.user.friends.add(user)
                return Response("Added as friend", status=status.HTTP_200_OK)

            user.invites.add(request.user)
            return Response("Added invite", status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    """
    Reject an invite
    """

    def delete(self, request, username=None):
        if not username:
            return Response(
                "Please provide a username", status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(username=username)
            if request.user.invites.filter(username=user.username):
                request.user.invites.remove(user)
                return Response("Removed user", status=status.HTTP_200_OK)
            return Response("Invite does not exist", status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                "User with provided username does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BlockedListView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request, username=None):
        try:
            blocked = request.user.blocked.all()
            return Response(
                UserSerializer_Username(blocked, many=True).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, username=None):
        if not username:
            return Response(
                "Please provide a username", status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(username=username)
            if request.user.blocked.filter(username=username):
                return Response("Already blocked", status=status.HTTP_400_BAD_REQUEST)
            if request.user == user:
                return Response(
                    "You cannot block yourself", status=status.HTTP_400_BAD_REQUEST
                )
            request.user.blocked.add(user)
            if request.user.invites.filter(username=username):
                request.user.invites.remove(user)
            if user.invites.filter(username=request.user.username):
                user.invites.remove(request.user)
            if request.user.friends.filter(username=username):
                request.user.friends.remove(user)
            return Response("Added blocked", status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username=None):
        if not username:
            return Response(
                "Please provide a username", status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(username=username)
            if request.user.blocked.filter(username=user.username):
                request.user.blocked.remove(user)
                return Response("Unblocked user", status=status.HTTP_200_OK)
            return Response("User is not blocked", status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                "User with provided username does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ColorView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        try:
            return Response(
                ColorsUserSerializer(request.user).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            user = request.user
            serializer = ColorUpdateSerializer(
                instance=user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Colors updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def user_exist_api(request, username=None):
    try:
        if username:
            User.objects.get(username=username)
            return Response(True, status=status.HTTP_200_OK)
        else:
            return Response(
                "Please provide a username", status=status.HTTP_400_BAD_REQUEST
            )
    except:
        return Response(False, status=status.HTTP_200_OK)


@api_view(["POST"])
@renderer_classes([JSONRenderer])
def user_login_api(request):
    try:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse(
                {"error": "Invalid username or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif not user.mailValidate:
            return JsonResponse(
                {"error": "Email not validated"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            login(request, user)
            return JsonResponse(
                {"message": "User created"}, status=status.HTTP_201_CREATED
            )
    except:
        return JsonResponse(
            {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@renderer_classes([JSONRenderer])
@login_required
def user_profile_pic_api(request, username=None):
    try:
        if username:
            user = get_object_or_404(User, username=username)
        else:
            user = request.user
        if user.profile_picture:
            path = user.profile_picture.path
            content_type, _ = mimetypes.guess_type(path)
            with open(path, "rb") as f:
                return HttpResponse(f.read(), content_type=content_type)
        default_image_path = os.path.join(settings.MEDIA_ROOT, "default_profile.png")
        with open(default_image_path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/png")
    except Exception as e:
        return JsonResponse({"error": e}, status=500)


ALLOWED_FILE_TYPES = ["image/jpeg", "image/png"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@api_view(["POST"])
@renderer_classes([JSONRenderer])
@login_required
def upload_profile_pic_api(request):
    try:
        if "profile_picture" in request.FILES:
            profile_picture = request.FILES["profile_picture"]

            # File type validation
            if profile_picture.content_type not in ALLOWED_FILE_TYPES:
                return JsonResponse({"error¬": "Invalid file type"}, status=400)

            # File size limit
            if profile_picture.size > MAX_FILE_SIZE:
                return JsonResponse(
                    {"error": "File size exceeds the limit"}, status=400
                )

            user = request.user

            # Check if the user already has a profile picture
            # if user.profile_picture:
            #     try:
            #         # Delete the old profile picture file from the storage
            #         if os.path.isfile(user.profile_picture.path):
            #             os.remove(user.profile_picture.path)
            #     except:
            #         pass

            # Save the new profile picture
            user.profile_picture = profile_picture
            user.save()
            return JsonResponse(
                {"message": "Upload successful"}, status=status.HTTP_201_CREATED
            )
        return JsonResponse(
            {"message": "No file found"}, status=status.HTTP_400_BAD_REQUEST
        )
    except ValidationError:
        return JsonResponse(
            {"error": "Invalid file"}, status=status.HTTP_400_BAD_REQUEST
        )
    except:
        return JsonResponse(
            {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
        )


def email_sent(request):
    return render(request, "html/email_sent.html")


def change_password(request):
    return render(request, "html/change_password.html")


def error404(request):
    return render(request, "html/error404.html")


def forgot_password(request):
    return render(request, "html/forgot_password.html")


@login_required
def account_information(request):
    return render(request, "html/accountInformation.html")


def logout_view(request):
    logout(request)
    return redirect("user_login")


@login_required
def test_upload(request):
    return render(request, "html/test_upload.html")


def profile_user(request, username=None):
    return render(request, "html/profile_user.html")


@login_required
def user_dashboard(request, username=None):
    user = request.user
    path = "html/dashboard.html"
    if username:
        user = User.objects.get(username=username)
        path = "html/profile_user.html"
    ratio_w = 0
    ratio_l = 0
    losses = user.total_games - user.wins
    if user.total_games != 0:
        ratio_w = round(user.wins / user.total_games * 100)
        ratio_l = round(losses / user.total_games * 100)
    return render(
        request,
        path,
        {
            "user": user,
            "losses": losses,
            "ratio_w": ratio_w,
            "ratio_l": ratio_l,
        },
    )


@api_view(["GET"])
def gameHistory_api(request, username):
    games = Game.objects.filter(gameuser__user__username=username, gamemode__gte=1, gamemode__lte=2)
    if not games:
        return JsonResponse({"historyGames": []}, status=status.HTTP_200_OK)
    historyGameList = []
    for game in games:
        maxPoint = 0
        dico = {
            "date": game.date.strftime('%Y-%m-%d'),
            "gamemode": game.gamemode,
            "users": [],
            "points": [],
        }
        gameusers = game.gameuser_set.all()
        for gameuser in gameusers:
            dico["users"].append(gameuser.user.username)
            dico["points"].append(gameuser.points)
            if gameuser.points > maxPoint:
                maxPoint = gameuser.points
        if maxPoint > 1:
            historyGameList.append(dico)
    return JsonResponse({"historyGames": historyGameList}, status=status.HTTP_200_OK)


def user_login(request):
    return render(request, "html/login.html")


def email_validated(request):
    return render(request, "html/email_validated.html")


def user_register(request):
    return render(request, "html/register.html")


@login_required
def social_management(request):
    return render(request, "html/socialManagement.html")


@login_required
def profile(request):
    return render(request, "profile.html")


@login_required
def dashboard(request):
    return render(request, "dashboard.html", {"user": request.user})


@api_view(["GET"])
@renderer_classes([JSONRenderer])
@login_required
def search_usernames_api(request, username=None):
    if username:
        MAX_RESULTS = 10
        matching_users = User.objects.filter(username__icontains=username)[:MAX_RESULTS]
        usernames = [user.username for user in matching_users]
        return JsonResponse({"usernames": usernames}, status=status.HTTP_200_OK)
    else:
        return JsonResponse(
            {"error": "Please provide a search term"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@renderer_classes([JSONRenderer])
@login_required
def profile_info_api(request, username=None):
    try:
        if username:
            user = get_object_or_404(User, username=username)
            serializer = OtherUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = PersonalUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return JsonResponse(
            {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@renderer_classes([JSONRenderer])
@login_required
def is_active_api(request, username=None):
    try:
        if username:
            user = get_object_or_404(User, username=username)
            cur_time = timezone.now()
            last_active = cur_time - user.last_active < timedelta(minutes=5)
            return Response(last_active, status=status.HTTP_200_OK)
        return Response(
            {"error": "Please provide a username"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except:
        return JsonResponse(
            {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
@renderer_classes([JSONRenderer])
@login_required
def update_profile_api(request):
    try:
        user = request.user

        new_username = request.data.get("username")
        new_email = request.data.get("email")

        if not new_username and not new_email:
            return Response(
                {"error": "You must provide either a new username or a new email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            new_username
            and new_username != user.username
            and User.objects.filter(username=new_username).exists()
        ):
            pass
        else:
            user.username = new_username
        if (
            new_email
            and new_email != user.email
            and User.objects.filter(email=new_email).exists()
        ):
            pass
        else:
            user.email = new_email

        user.save()
        return Response(
            {"message": "User information updated successfully."},
            status=status.HTTP_200_OK,
        )
    except:
        return JsonResponse(
            {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
@renderer_classes([JSONRenderer])
@login_required
def change_password_api(request):
    try:
        user = request.user
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")

        if not user.check_password(old_password):
            return JsonResponse(
                {"error": "Old password is incorrect"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if old_password == new_password:
            return JsonResponse(
                {"error": "New password must be different from the old one"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            password_validation.validate_password(new_password, user=user)
        except ValidationError as e:
            return JsonResponse(
                {"error": e.messages}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)
        return JsonResponse(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return JsonResponse(
            {"error": "Bad request"}, status=status.HTTP_400_BAD_REQUEST
        )


@login_required
def test_password_change_view(request):
    return render(request, "test_password_change.html")


def MessageContentPwd(user):
    subject = "Reset password"
    GenerateUserToken(user, mail=False)
    ResetLink = (
        "https://10.11.13.4/api/reset_password/" + user.username + "/" + user.token
    )
    mailContent = f"""
    <h1>Hi {user.username}!</h1>
    <p>To reset your password, simply click this link :
    <a href="{ResetLink}">Reset Password</a></p>

    DO NOT REPLY.
    """
    return subject, mailContent


def MessageContentMail(user):
    subject = "Mail Validation"
    GenerateUserToken(user, mail=True)
    ValidateLink = "https://10.11.13.4/api/mail/" + user.username + "/" + user.token
    mailContent = f"""
    <h1>Welcome to transcendance {user.username}!</h1>
    <p>To validate your email, simply click this link :
    <a href="{ValidateLink}">Mail validation</a></p>

    DO NOT REPLY.
    """
    return subject, mailContent


def sendMail(user, mail, isMail=False):
    smtp_server = "mail.infomaniak.com"
    smtp_port = 587
    smtp_user = os.environ.get("MAIL_USER")
    smtp_password = os.environ.get("MAIL_PWD")
    subject, content = MessageContentMail(user) if isMail else MessageContentPwd(user)

    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(content, "html"))
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = mail
    msg.attach(MIMEText(content, "html"))
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, mail, msg.as_string())
    server.quit()
    return True
    # try:
    #     server.sendmail(smtp_user, mail, msg.as_string())
    #     server.quit()
    #     return True
    # except:
    #     server.quit()
    #     return False


def GenerateUserToken(user, mail=False):
    from random import choice, randint

    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcefghijklmnopqrstuvwxyz1234567890-_"
    tokenListe = User.objects.values_list("token", flat=True)
    while True:
        token = "M" if mail else "P"
        for i in range(22):
            token += choice(characters)
        if token not in tokenListe:
            break
    user.token = token
    user.save()


def EmailValidation(request, username, token):
    print("EMAIL VALIDATION !!!!!!!!!!!!!!!!!!!!")
    users = User.objects.filter(username=username)
    if users.exists():
        user = users.first()
    else:
        raise Http404("Invalid link")
    if not token or user.token != token:
        print("WRONG DATA")
        raise Http404("Invalid link")
    else:
        user.mailValidate = True
        user.token = ""
        user.save()
        return render(request, "html/email_validated.html")


class sendPasswordReset(APIView):
    def get(self, request):
        return render(request, "html/forgot_password.html")

    def post(self, request):
        mail = request.data.get("email")
        if not mail:
            return Response({"message": "No mail"}, status=status.HTTP_400_BAD_REQUEST)
        elif not User.objects.filter(email=mail).exists():
            return Response(
                {"message": "Invalide mail"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(email=mail).first()
        if not sendMail(user, mail, isMail=False):
            return Response(
                {"message": "Invalid mail"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"success": True}, status=status.HTTP_200_OK)


def PasswordForgot(request, username=None, token=None):
    users = User.objects.filter(username=username)
    if not users:
        print("USER NOT FOUND")
        raise Http404("Invalide link")
    user = users.first()
    if not token or token != user.token:
        print("INVALIDE TOKEN :", user.token)
        raise Http404("Invalide link")
    return render(
        request, "html/change_password.html", {"token": token, "username": username}
    )


@api_view(["POST"])
def PasswordReset(request):
    username = request.data.get("username")
    token = request.data.get("token")
    new_password = request.data.get("new_password")
    if not username or not token:
        return Response(
            {"error": "Invalide arguments"}, status=status.HTTP_400_BAD_REQUEST
        )
    users = User.objects.filter(username=username)
    if not new_password:
        return Response({"error": "No password"}, status=status.HTTP_400_BAD_REQUEST)
    if users.exists():
        user = users.first()
    else:
        raise Http404("Invalide link")
    if not token or user.token != token:
        raise Http404("Invalide link")
    else:
        try:
            password_validation.validate_password(new_password, user=user)
        except ValidationError as e:
            return JsonResponse(
                {"error": e.messages}, status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.token = ""
        user.save()

        return Response(
            {"success": True}, status=status.HTTP_200_OK
        )  # TODO Redirection


def handler404(request, exception):
    return render(request, "html/error404.html", status=404)
