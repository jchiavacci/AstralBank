from django.db import models
from items.models import Expansion
from player.models import Character

REWARD_TYPES = (
    ('mount', 'Mount'),
    ('cosmetic', 'Cosmetic'),
    ('toy', 'Toy'),
    ('other', 'Other')
)

class Prize(models.Model):
    prizeName = models.CharField(max_length=100, null=True)
    expansion = models.ForeignKey(Expansion, models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=10, choices=REWARD_TYPES)
    points = models.IntegerField(null=True)

    def __str__(self):
        if self.prizeName is None:
            name = "PRIZE NAME MISSING"
        else:
            name = self.prizeName
        return "{0}".format(name)

class Reward(models.Model):
    time = models.DateTimeField()
    character = models.ForeignKey(Character, models.SET_NULL, null=True)
    prize = models.ForeignKey(Prize, models.SET_NULL, null=True)

    def __str__(self):
        if self.character is None:
            characterName = "CHARACTER MISSING"
        else:
            characterName = self.character
        return "{0} receives: {1}".format(characterName, self.prize)

    def save(self, *args, **kwargs):
        self.character.player.points -= self.prize.points
        self.character.player.save()
        super(Reward, self).save(args, kwargs)

