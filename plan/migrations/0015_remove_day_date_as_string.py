# Generated by Django 4.0.3 on 2023-08-06 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0014_alter_day_date_as_string'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='day',
            name='date_as_string',
        ),
    ]
