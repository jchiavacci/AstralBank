from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)
    points = models.IntegerField()
    def __str__(self):
        return "{0}".format(self.name)


class Character(models.Model):
    name = models.CharField(max_length=100, unique=True)
    player = models.ForeignKey(Player, models.SET_NULL, related_name="player_characters", null=True)
    def __str__(self):
        return "{0} ({1})".format(self.player.name, self.name)




