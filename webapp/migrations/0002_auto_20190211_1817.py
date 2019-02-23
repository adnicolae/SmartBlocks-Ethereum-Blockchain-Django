# Generated by Django 2.1.3 on 2019-02-11 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='contract',
        ),
        migrations.AddField(
            model_name='offer',
            name='price',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=30),
        ),
        migrations.AddField(
            model_name='offer',
            name='quantity',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='offer',
            name='completion_condition',
            field=models.CharField(help_text="Keywords: <span class='keyword'>AND</span>, <span class='keyword'>OR</span>.</br>Operations: <, >, =</br>Variables: <span class='variable'>price</span>, <span class='variable'>quantity</span></br>Use parentheses to group statements.</br></br>Example:</br> (<span class='variable'>price</span> < 100 <span class='keyword'>AND</span> (<span class='variable'>quantity</span> > 20 <span class='keyword'>AND</span> <span class='variable'>quantity</span> < 50)) </br><span class='keyword'>OR</span> (<span class='variable'>price</span> < 120 <span class='keyword'>AND</span> <span class='variable'>quantity</span> < 20)", max_length=256),
        ),
    ]