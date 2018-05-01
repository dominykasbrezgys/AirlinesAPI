# Generated by Django 2.0.2 on 2018-02-27 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airline', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='passenger',
            name='email',
            field=models.EmailField(default='None', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='flight',
            name='duration',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='flight',
            name='seatCost',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='flight',
            name='seatPrice',
            field=models.FloatField(),
        ),
    ]