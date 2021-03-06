# Generated by Django 2.1.3 on 2019-04-27 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webapp', '0013_auto_20190425_1955'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.CharField(max_length=256)),
                ('private_key', models.CharField(max_length=256)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='offer',
            name='encrypted_contract_buyer',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='encrypted_contract_seller',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
