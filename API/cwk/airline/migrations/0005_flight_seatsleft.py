# Generated by Django 2.0.2 on 2018-02-28 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airline', '0004_auto_20180228_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='seatsLeft',
            field=models.IntegerField(default=150),
        ),
    ]