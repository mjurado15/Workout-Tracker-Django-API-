# Generated by Django 5.1.2 on 2024-10-23 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0007_remove_scheduledworkoutdate_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurringworkoutalert',
            name='activated',
        ),
        migrations.RemoveField(
            model_name='scheduledworkoutdate',
            name='activated',
        ),
    ]