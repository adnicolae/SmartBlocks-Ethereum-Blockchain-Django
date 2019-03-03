# Generated by Django 2.1.3 on 2019-03-03 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_auto_20190303_1421'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='priceHigh',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='priceLow',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='quantHigh',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='quantLow',
        ),
        migrations.AddField(
            model_name='offer',
            name='bounds',
            field=models.CharField(default='[0,2147483648,0,2147483648]', max_length=256),
        ),
    ]