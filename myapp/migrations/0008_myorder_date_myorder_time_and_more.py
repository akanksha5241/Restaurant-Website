# Generated by Django 4.2.3 on 2024-02-03 17:52

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_myorder_food_item_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='myorder',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='myorder',
            name='time',
            field=models.TimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='myorder',
            name='food_item_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='myorder',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name='myorder',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name='myorder',
            name='total_price',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
