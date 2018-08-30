from django.db import models
import csv, io, os
from datetime import datetime
from django.db import models
from items.models import Item
from player.models import Character

TRANSACTION_TYPES = (
    ('deposit', 'Deposit'),
    ('withdraw', 'Withdraw'),
    ('move', 'Move'),
    ('repair', 'Repair')
)

# LINE FORMAT:
# REALM, FACTION, GUILD, SCAN TIME, TRANSACTION TIME, TAB NUMBER, TAB NAME, TRANSACTION TYPE, UNIT NAME, ITEM NAME, ITEM ID, ITEM COUNT
class Transaction(models.Model):
    time = models.DateTimeField()
    character = models.ForeignKey(Character, models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    item = models.ForeignKey(Item, models.SET_NULL, null=True)
    quantity = models.IntegerField()
    processed = models.BooleanField(default=False)
    error_message = models.CharField(max_length=500, null=True)

    def __str__(self):
        if self.item is None:
            item = "ITEM NAME MISSING"
        else:
            item = self.item.itemId
        return "{0} {1} {2} itemId: {3}".format(self.character, self.type, self.quantity, item)

    def process(self):
        if self.processed is False:
            if self.character is not None:
                if self.character.player is not None:
                    if self.item is not None:
                        if self.item.points is not None:
                            if self.type == 'deposit':
                                self.character.player.points += self.item.points * self.quantity
                                self.character.player.save()
                                self.processed = True
                                self.error_message = ""
                                self.save()
                        else:
                            self.error_message = "Item has no point value assigned"
                            self.save()
                    else:
                        self.error_message = "Item does not exist"
                        self.save()
                else:
                    self.error_message = "Character has no player assigned"
                    self.save()
            else:
                self.error_message = "Character does not exist"
                self.save()

    def revert(self):
        if self.processed is True:
            if self.character is not None:
                if self.character.player is not None:
                    if self.item is not None:
                        if self.item.points is not None:
                            if self.type == 'deposit':
                                self.character.player.points -= self.item.points * self.quantity
                                self.character.player.save()


class TransactionFileQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            f = io.TextIOWrapper(obj.file.file.file, encoding='UTF-8')
            transactions = csv.reader(f)
            for line in transactions:
                transaction = Transaction.objects.filter(time=datetime.fromtimestamp(int(line[4])).strftime("%Y-%m-%d %H:%M:%S")).filter(character__name=line[8].strip()).filter(type=line[7].strip()).filter(item__itemId=line[10]).filter(quantity=int(line[11]))
                if transaction.first() is not None:
                    transaction.first().revert()
                    transaction.first().delete()
        super(TransactionFileQuerySet, self).delete(*args, **kwargs)

class TransactionFile(models.Model):
    objects = TransactionFileQuerySet.as_manager()
    file = models.FileField(unique=True)

    class Meta:
        verbose_name = "file"
        verbose_name_plural = "files"

    def __str__(self):
         return "{0}".format(os.path.basename(self.file.name))

    def save(self, *args, **kwargs):
        f = io.TextIOWrapper(self.file.file.file, encoding='UTF-8')
        transactions = csv.reader(f)
        for line in transactions:
            input_data = Transaction()
            input_data.error_message = ""
            #input_data.time = datetime.strptime(line[4], "%Y/%m/%d %H:%M:%S")
            input_data.time = datetime.fromtimestamp(int(line[4])).strftime("%Y-%m-%d %H:%M:%S")
            char = Character.objects.filter(name=line[8].strip())
            if char.exists():
                input_data.character = char.first()
            else:
                character = Character(name=line[8].strip())
                character.save()
                input_data.character = character
                input_data.error_message += "No existing character. "
            input_data.type = line[7].strip()
            item = Item.objects.filter(itemId=line[10])
            if item.exists():
                input_data.item = item.first()
            else:
                new_item = Item(itemId=line[10], itemName=line[9].strip())
                new_item.save()
                input_data.item = new_item
                input_data.error_message += "No existing item."
            if input_data.item.itemId == 0:
                #Its gold. Divide by 10000 to switch from gold val to copper val
                #As per terra, round up.
                if int(line[11]) % 10000 != 0:
                    input_data.quantity = (int(line[11]) / 10000) + 1;
                else:
                    input_data.quantity = int(line[11]) / 10000
            else:
                input_data.quantity = int(line[11])
            input_data.save()
            input_data.process()

        super(TransactionFile, self).save(args, kwargs)
