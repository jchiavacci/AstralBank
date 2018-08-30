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
    itemId = models.BigIntegerField(unique=True, primary_key=True)
    itemName = models.CharField(max_length=100, null=True)
    category = models.ForeignKey(Category, models.SET_NULL, null=True, blank=True)
    expansion = models.ForeignKey(Expansion, models.SET_NULL, blank=True, null=True)
    points = models.IntegerField(null=True)

    #Overwriting init like this lets us save the original value so we can smart update transactions
    __original_points = None

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self.__original_points = self.points

    def __str__(self):
        if self.itemName is None:
            name = "NO NAME"
        else:
            name = self.itemName
        return "{0} ({1})".format(name, self.itemId)

    def save(self, *args, **kwargs):
        from transactions.models import Transaction
        super(Item, self).save(args, kwargs)
        if self.points != self.__original_points:
            queryset = Transaction.objects.filter(processed=False).filter(item__itemId=self.itemId)
            for t in queryset:
                t.process()




