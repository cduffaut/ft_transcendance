
from django.urls import path, include
from .views import home_page, gamePage, newGame, apiGetGame

urlpatterns = [
    path('home/', home_page, name='home_page'),
    path('onlineGame/', newGame.as_view(), name='online_game'),
    path('newGame/', newGame.as_view(), name='newGame'),
    path('game/<int:id>/', gamePage, name="gamePage"),
    path('api/game/<int:gameid>/', apiGetGame, name="getGame")
]
