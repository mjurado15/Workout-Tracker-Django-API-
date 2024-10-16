from django.db import models
from django.utils import timezone

from apps.users.models import User


class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Exercise Category"
        verbose_name_plural = "Exercise Categories"

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        ExerciseCategory, on_delete=models.CASCADE, related_name="exercises"
    )

    def __str__(self):
        return self.name


class WorkoutPlan(models.Model):
    STATUS_CHOICES = [
        ("active", "active"),
        ("pending", "pending"),
        ("finished", "finished"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="workout_plans"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Workout Plan"
        verbose_name_plural = "Workout Plans"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # set status field to "active" updates the started_at field to the current date only the first time
        if self.status == "active" and self.started_at is None:
            self.started_at = timezone.now()

        # changing the status field to "finished" updates the finished_at field each time
        # Get the original instance of the object if it already exists in the DB
        if self.pk:
            original = WorkoutPlan.objects.get(pk=self.pk)
        else:
            original = None

        if self.status == "finished" and (
            original is None or original.status != "finished"
        ):
            self.finished_at = timezone.now()

        return super().save(*args, **kwargs)
