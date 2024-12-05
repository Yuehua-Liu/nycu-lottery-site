# Generated by Django 4.2.3 on 2024-12-03 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='email',
        ),
        migrations.RemoveField(
            model_name='prize',
            name='description',
        ),
        migrations.AlterField(
            model_name='participant',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='prize',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
