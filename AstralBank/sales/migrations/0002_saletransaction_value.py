# Generated by Django 2.0.2 on 2018-12-07 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='saletransaction',
            name='value',
            field=models.IntegerField(null=True),
        ),
    ]
