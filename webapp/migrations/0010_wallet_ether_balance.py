# Generated by Django 2.1.7 on 2019-03-03 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0009_auto_20190303_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='ether_balance',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
    ]
