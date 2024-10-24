# Generated by Django 5.1.2 on 2024-10-22 05:15

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0002_workout_exerciseplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkoutComment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='workouts.workout')),
            ],
        ),
    ]
