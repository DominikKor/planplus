# Generated by Django 4.0.3 on 2023-08-06 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0013_alter_period_room_alter_teacher_last_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='date_as_string',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
