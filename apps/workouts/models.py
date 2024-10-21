import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class ExerciseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("exercise category")
        verbose_name_plural = _("exercise categories")

    def __str__(self):
        return self.name


class Exercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        ExerciseCategory, on_delete=models.CASCADE, related_name="exercises"
    )

    def __str__(self):
        return self.name


class ExercisePlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="exercise_plans"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    sets = models.IntegerField(null=True, blank=True)
    reps = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    weight_measure_unit = models.CharField(max_length=50, blank=True)

    workout = models.ForeignKey(
        "workouts.Workout",
        on_delete=models.CASCADE,
        related_name="exercise_plans",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("exercise plan")
        verbose_name_plural = _("exercise plans")

    def __str__(self):
        return f"{self.name} - {self.exercise.name} ({self.workout.name})"


class Workout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workouts")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user})"
