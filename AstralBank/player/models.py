from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)
    points = models.IntegerField()
    def __str__(self):
        return "{0}".format(self.name)

    def getTransactions(self):
        from transactions.models import Transaction
        characters = Character.objects.filter(player__name=self.name)
        for c in characters:
            queryset = Transaction.objects.filter(character__name=c.name) |  queryset
        return queryset



class Character(models.Model):
    name = models.CharField(max_length=100, unique=True)
    player = models.ForeignKey(Player, models.SET_NULL, related_name="player_characters", null=True)
    def __str__(self):
        if self.player is None:
            name = "NO PLAYER ASSIGNED"
        else:
            name = self.player.name
        return "{0} ({1})".format(name, self.name)

    __original_player = None
    def __init__(self, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self.__original_player = self.player

    def save(self, *args, **kwargs):
        from transactions.models import Transaction
        super(Character, self).save(args, kwargs)
        if self.player != self.__original_player:
            queryset = Transaction.objects.filter(processed=False).filter(character__player__name=self.player)
            for t in queryset:
                t.process()




