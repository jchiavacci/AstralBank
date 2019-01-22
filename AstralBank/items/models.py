from django.db import models
import csv, io, os


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

class ItemFile(models.Model):
    file = models.FileField(unique=True)

    class Meta:
        verbose_name = "file"
        verbose_name_plural = "files"

    def __str__(self):
        return "{0}".format(os.path.basename(self.file.name))

    def save(self, *args, **kwargs):
        f = io.TextIOWrapper(self.file.file.file, encoding='UTF-8')
        items = csv.reader(f)
        for line in items:
            input_data = Item()
            item = Item.objects.filter(itemId=line[0])
            if item.exists():
                input_data = item.first()
                #Its gold. Divide by 10000 to switch from gold val to copper val
                #As per terra, round up.
                if int(line[2]) < 10000:
                    input_data.points = 1;
                elif int(line[2]) % 10000 != 0:
                    input_data.points = (int(line[2]) / 10000) + 1;
                else:
                    input_data.points = int(line[2]) / 10000
            else:
                #Its gold. Divide by 10000 to switch from gold val to copper val
                #As per terra, round up.
                points = 1
                if int(line[2]) < 10000:
                    points = 1
                elif int(line[2]) % 10000 != 0:
                    points = (int(line[2]) / 10000) + 1
                else:
                    points = int(line[2]) / 10000
                input_data = Item(itemId=int(line[0]), itemName=line[1].strip(), points=points)
            input_data.save()
        super(ItemFile, self).save(args, kwargs)




