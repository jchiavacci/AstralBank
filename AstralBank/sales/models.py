from django.db import models
from django.db.models.signals import m2m_changed
from player.models import Player

class Sale(models.Model):
    time = models.DateTimeField()
    players = models.ManyToManyField(Player, related_name='sale_players', null=True)
    value = models.IntegerField(null=True)
    name = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=100, null=True)

    def __str__(self):
        if self.name is None:
            name = "SALE NAME MISSING"
        else:
            name = self.name
        return "{0}".format(name)


class SaleTransaction(models.Model):
    player = models.ForeignKey(Player, models.SET_NULL, null=True)
    sale = models.ForeignKey(Sale, models.SET_NULL, null=True)
    value = models.IntegerField(null=True)

    def reverse(self):
        self.player.points -= self.value
        self.player.save()

    def process(self):
        self.player.points += self.value
        self.player.save()

    def save(self, *args, **kwargs):
        self.process()
        super(SaleTransaction, self).save(args, kwargs)

    def delete(self, *args, **kwargs):
        self.reverse()
        super(SaleTransaction, self).delete(args, kwargs)

    def __str__(self):
        if self.sale is None:
            name = "SALE NAME MISSING"
        else:
            name = self.sale.name
        if self.player is None:
            playerName = "PLAYER NAME MISSING"
        else:
            playerName = self.player.name
        return "{0} - {1}".format(playerName, name)

def characters_changed(sender, **kwargs):
    theSale = kwargs.pop("instance")
    pk_set = kwargs.pop("pk_set")
    isReverse = kwargs.pop("reverse")
    action = kwargs.pop("action")
    if (action == 'pre_add') or (action == 'pre_remove'):
        #On pre add/remove.. take the current set. REverse saletransactions.
        print(theSale.players.all())
        transactions = SaleTransaction.objects.filter(sale=theSale.id).all()
        if transactions is not None:
            for transaction in transactions:
                transaction.delete()

    if (action == 'post_add') or (action == 'post_remove'):
        print("REMOVED?")
        #On post add/remove.. take the new set. calculate share and make new saletransactions
        numChars = theSale.players.all().count()
        intVal = int(theSale.value)
        dividedValue = ((intVal + (numChars - 1)) / numChars)
        for player in theSale.players.all():
            saleTrans = SaleTransaction()
            saleTrans.player = player
            saleTrans.value = dividedValue
            saleTrans.sale = theSale
            print("B")
            saleTrans.save()
        print(theSale.players.all())

    print(theSale)
    print(pk_set)
    print(isReverse)
    pass

m2m_changed.connect(characters_changed, sender=Sale.players.through)
