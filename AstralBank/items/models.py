from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return "{0}".format(self.name)


class Expansion(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return "{0}".format(self.name)


class Item(models.Model):
    itemId = models.BigIntegerField(unique=True)
    category = models.ForeignKey(Category, models.SET_NULL, null=True, blank=True)
    expansion = models.ForeignKey(Expansion, models.SET_NULL, blank=True, null=True)
    points = models.IntegerField(null=True)

    def __str__(self):
        return "{0}".format(self.itemId)


