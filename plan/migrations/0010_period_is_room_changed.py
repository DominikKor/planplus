# Generated by Django 4.0.3 on 2022-05-20 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0009_alter_period_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='is_room_changed',
            field=models.BooleanField(default=False),
        ),
    ]
