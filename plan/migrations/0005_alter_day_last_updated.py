# Generated by Django 4.0.3 on 2022-03-27 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0004_day_last_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='last_updated',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
