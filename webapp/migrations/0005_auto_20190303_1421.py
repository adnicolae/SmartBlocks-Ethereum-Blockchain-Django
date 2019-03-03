# Generated by Django 2.1.3 on 2019-03-03 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='priceHigh',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=30),
        ),
        migrations.AddField(
            model_name='offer',
            name='priceLow',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=30),
        ),
        migrations.AddField(
            model_name='offer',
            name='quantHigh',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='offer',
            name='quantLow',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
    ]
