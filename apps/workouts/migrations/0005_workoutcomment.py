# Generated by Django 5.1.2 on 2024-10-17 21:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0004_exerciseplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkoutComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workout_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='workouts.workoutplan')),
            ],
        ),
    ]
