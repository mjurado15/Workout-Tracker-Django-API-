# Generated by Django 5.1.2 on 2024-10-22 19:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0004_workout_type_recurringworkoutdays_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecurringWorkoutDays',
            new_name='RecurringWorkoutAlert',
        ),
    ]