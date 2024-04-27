from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from user.models import User
from tournament.models import Tournament

class Game(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    ballwidth = models.FloatField(default=0.1, validators=[MinValueValidator(0.05), MaxValueValidator(0.3)])
    planksize = models.FloatField(default=0.3, validators=[MinValueValidator(0.1), MaxValueValidator(0.4)])
    Speed = models.FloatField(default=1, validators=[MinValueValidator(0.05), MaxValueValidator(0.3)])
    acceleration = models.FloatField(default=1, validators=[MinValueValidator(0.0), MaxValueValidator(0.1)]) #TODO Right value
    winpoint = models.PositiveIntegerField(default=5, validators=[MinValueValidator(3), MaxValueValidator(15)])
    gamemode = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)]) #0 offline, 1 2p, 2 4p, 3 IA
    nextGame = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    gameRunning = models.BooleanField(default=False)
    gameLevel = models.PositiveIntegerField(default=0) # level in tournament tree view
    levelPos = models.PositiveIntegerField(default=0) # position in level

class GameUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, default=None)
    points = models.PositiveIntegerField(default=0)