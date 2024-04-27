from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    token = models.CharField(max_length=255, blank=True)
    mailValidate = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_active = models.DateTimeField(default=timezone.now)
    wins = models.PositiveIntegerField(default=0, verbose_name="Number of wins")
    ball_color = models.CharField(max_length=7, default="#FFFFFF")
    paddle_color = models.CharField(max_length=7, default="#FFFFFF")
    enemy_paddle_color = models.CharField(max_length=7, default="#FFFFFF")
    frame_color = models.CharField(max_length=7, default="#FFFFFF")
    background_color = models.CharField(max_length=7, default="#000000")
    total_games = models.PositiveIntegerField(
        default=0, verbose_name="Total number of games"
    )
    tournaments_wins = models.PositiveIntegerField(default=0, verbose_name="Number of tournaments wins")
    total_tournaments = models.PositiveIntegerField(default=0, verbose_name="Total number of tournaments")
    friends = models.ManyToManyField("self", symmetrical=True)
    blocked = models.ManyToManyField(
        "self", symmetrical=False, related_name="blocked_by"
    )
    invites = models.ManyToManyField(
        "self", symmetrical=False, related_name="sent_invites"
    )
    profile_picture = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    objects = CustomUserManager()
    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username
