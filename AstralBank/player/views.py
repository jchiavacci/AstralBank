from django.shortcuts import render
from player.models import Player

def home(request):
    top_players = Player.objects.order_by("-points").exclude(name="Ayegon").exclude(name="Terra")[:5]
    return render(request, "player/home.html",
        {'players' : top_players})
