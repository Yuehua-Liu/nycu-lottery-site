# Generated by Django 4.2.3 on 2024-12-05 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0003_prize_order_prize_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='prize',
            name='remaining',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
