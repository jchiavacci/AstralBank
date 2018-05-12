from django.db import models
import csv, io, os
from datetime import datetime
from django.db import models
from items.models import Item
from player.models import Character

TRANSACTION_TYPES = (
    ('deposit', 'Deposit'),
    ('withdraw', 'Withdraw')
)


class Transaction(models.Model):
    time = models.DateTimeField()
    character = models.ForeignKey(Character, models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    item = models.ForeignKey(Item, models.SET_NULL, null=True)
    quantity = models.IntegerField()
    processed = models.BooleanField(default=False)
    error_message = models.CharField(max_length=500, null=True)

    def __str__(self):
        return "{0} {1} {2} itemId:{3}".format(self.character, self.type, self.quantity, self.item.itemId)


class TransactionFile(models.Model):
    file = models.FileField(unique=True)

    def __str__(self):
         return "{0}".format(os.path.basename(self.file.name))

    def delete(self, 
    def save(self, *args, **kwargs):
        f = io.TextIOWrapper(self.file.file.file, encoding='UTF-8')
        transactions = csv.reader(f)
        for line in transactions:
            input_data = Transaction()
            input_data.error_message = ""
            input_data.time = datetime.strptime(line[0], "%Y/%m/%d %H:%M:%S")
            char = Character.objects.filter(name=line[1])
            if char.exists():
                input_data.character = char.first()
            else:
                input_data.character = Character(name=line[1])
                input_data.error_message += "No existing character. "
            input_data.type = line[2]
            item = Item.objects.filter(itemId=line[3])
            if item.exists():
                input_data.item = item.first()
            else:
                input_data.item = Item(itemId=line[3])
                input_data.error_message += "No existing item."
            input_data.quantity = line[4]
            input_data.save()
        super(TransactionFile, self).save(args, kwargs)