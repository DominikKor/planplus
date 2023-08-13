# Generated by Django 4.0.3 on 2023-08-06 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0011_period_is_subject_changed'),
    ]

    operations = [
        migrations.AddField(
            model_name='day',
            name='date_as_string',
            field=models.CharField(default=models.DateField(), max_length=100),
        ),
        migrations.AddField(
            model_name='period',
            name='change_info',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]