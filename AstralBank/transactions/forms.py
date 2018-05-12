from django.forms import ModelForm, forms
import csv
import datetime
from .models import Transaction, Character, Item


class TransactionForm(ModelForm):
    class Meta:
        model = TransactionForm
        fields = ('file',)
    def parse_transactions(f):
        transactions = csv.reader(f)
        for line in transactions:
            input_data = Transaction()
            input_data.error_message = ""
            input_data.time = datetime.strptime(line[0], "%y/%m/%d %H:%M:%S")
            char = Character.filter(name=line[1])
            if char.exists():
                input_data.character = char.first()
            else:
                input_data.character = Character(name=line[1])
                input_data.error_message += "No existing character. "
            input_data.type = line[2]
            item = Item.filter(itemId=line[3])
            if item.exists():
                input_data.item = item.first()
            else:
                input_data.item = Item(itemId=line[3])
                input_data.error_message += "No existing item."
            input_data.quantity = line[4]