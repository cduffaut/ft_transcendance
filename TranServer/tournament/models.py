from django.db import models
from user.models import User
# from game.models import Game

class Tournament(models.Model):
    playerNumber = models.PositiveIntegerField(default=0)