# Generated by Django 4.0.3 on 2022-05-26 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0010_period_is_room_changed'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='is_subject_changed',
            field=models.BooleanField(default=False),
        ),
    ]
