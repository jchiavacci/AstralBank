from django.db import models
import csv, io, os, requests, pickle
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone
from items.models import Item
from player.models import Character
from filelock import Timeout, FileLock

TRANSACTION_TYPES = (
    ('deposit', 'Deposit'),
    ('withdraw', 'Withdraw'),
    ('move', 'Move'),
    ('repair', 'Repair')
)
file_path = "./api_response.json"
lock_path = "./api_response.json.lock"

#itemDict = {'items': {}, 'lastUpdateTime': timezone.now() - timedelta(days=60)}

def refreshItemPrices():
    lock = FileLock(lock_path, timeout=5)
    try:
        with lock.acquire(timeout=10):
            try:
                itemDict = pickle.loads(open(file_path, "rb").read())
            except FileNotFoundError:
                itemDict = {'items': {}, 'lastUpdateTime': timezone.now() - timedelta(days=60)}
                open(file_path, "wb+").write(pickle.dumps(itemDict))
            if itemDict['lastUpdateTime'] < timezone.now() - timedelta(days=7):
                r = requests.get('http://api.tradeskillmaster.com/v1/item/US/turalyon?format=json&fields=Id%2CName%2CMarketValue&apiKey=bKpCvS_Zidc8BoUie7h29g6OhJ23ki5I')
                itemList = r.json()
                # itemList = [{'Id': 152494, 'MarketValue': 690067, 'Name': 'Coastal Healing Potion 69' }]
                newItemDict = {'items': {}, 'lastUpdateTime': timezone.now()}
                for item in itemList:
                    points = 1
                    value = item.get('MarketValue')
                    if value < 10000:
                        points = 1
                    elif value % 10000 != 0:
                        points = (value / 10000) + 1
                    else:
                        points = value / 10000
                    newItemDict['items'][item.get('Id')] = {'Name': item.get('Name'), 'MarketValue': points}
                newItemDict['lastUpdateTime'] = timezone.now()
                open(file_path, "wb").write(pickle.dumps(newItemDict))
                itemDict = newItemDict
            return itemDict
    except Timeout:
        pass

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
            if self.type == 'deposit':
                if self.character is not None:
                    if self.character.player is not None:
                        if self.item is not None:
                            if self.item.itemId == 0:
                                #It's gold
                                self.character.player.points += self.quantity
                                self.character.player.save()
                                self.processed = True
                                self.error_message = ""
                                self.save()
                            elif self.item.points is not None:
                                itemDict = refreshItemPrices()
                                if self.item.updated < timezone.now() - timedelta(minutes=1):
                                    if self.item.itemId in itemDict['items']:
                                        newPoints = itemDict['items'][self.item.itemId].get('MarketValue')
                                        self.item.points = newPoints
                                        self.item.save()
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
            if self.type == 'deposit':
                if self.character is not None:
                    if self.character.player is not None:
                        if self.item is not None:
                            if self.item.itemId == 0:
                                #It's gold
                                self.character.player.points -= self.quantity
                                self.character.player.save()
                            elif self.item.points is not None:
                                self.character.player.points -= self.item.points * self.quantity
                                self.character.player.save()


class TransactionFileQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            f = io.TextIOWrapper(obj.file.file.file, encoding='UTF-8')
            transactions = csv.reader(f)
            for line in transactions:
                goldVal = 0
                if int(line[10]) == 0:
                #Its gold. Divide by 10000 to switch from gold val to copper val
                #As per terra, round up.
                    if int(line[11]) < 10000:
                        goldVal = 1
                    elif int(line[11]) % 10000 != 0:
                        goldVal = (int(line[11]) / 10000) + 1
                    else:
                        goldVal = int(line[11]) / 10000
                else:
                    goldVal = int(line[11])
                transaction = Transaction.objects.filter(time=datetime.fromtimestamp(int(line[4])).strftime("%Y-%m-%d %H:%M:%S")).filter(character__name=line[8].strip()).filter(type=line[7].strip()).filter(item__itemId=line[10]).filter(quantity=goldVal)
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
        itemDict = refreshItemPrices()

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
                itemId = int(line[10])
                if itemId in itemDict['items'].keys():
                    new_item.points = itemDict['items'][itemId].get('MarketValue')
                else:
                    input_data.error_message = "Item ID " + line[10] + " not seen before, and not present in TSM response"
                new_item.save()
                input_data.item = new_item
            if input_data.item.itemId == 0:
                #Its gold. Divide by 10000 to switch from gold val to copper val
                #As per terra, round up.
                if int(line[11]) < 10000:
                    input_data.quantity = 1;
                elif int(line[11]) % 10000 != 0:
                    input_data.quantity = (int(line[11]) / 10000) + 1;
                else:
                    input_data.quantity = int(line[11]) / 10000
            else:
                input_data.quantity = int(line[11])
            input_data.save()
            input_data.process()

        super(TransactionFile, self).save(args, kwargs)
