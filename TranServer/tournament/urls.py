from django.urls import path, include
# from .views import tournament_settings
# from .views import bracket
from .views import tournamentSettings, TournamentView, TournamentJoin #, TournamentAddUser
from django.urls import path
from . import views

urlpatterns = [
        # path ('tournamentSettings/', tournament_settings, name='tournament_settings'),
        # path ('bracket/', bracket, name='bracket'),
        path ('tournament/Settings/', tournamentSettings.as_view(), name='tournamentSettings'),
        path('tournament/<int:id>/', TournamentView.as_view(), name='TournamentView'),
        path('tournament/<int:id>/join/', TournamentJoin.as_view(), name='TournamentJoin'),
        # path('tournament/adduser/<int:id>/', TournamentAddUser, name='TournamentAddUser'),
]