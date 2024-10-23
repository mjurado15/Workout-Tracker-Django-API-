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

    SCHEDULED = "S"
    RECURRENT = "R"

    WORKOUT_TYPE = [
        (SCHEDULED, "scheduled"),
        (RECURRENT, "recurrent"),
    ]

    type = models.CharField(max_length=10, choices=WORKOUT_TYPE, blank=True)

    def __str__(self):
        return f"{self.name} ({self.user})"

    def is_recurrent(self):
        return self.type == self.RECURRENT

    def is_scheduled(self):
        return self.type == self.SCHEDULED

    def switch_to_recurrent(self):
        self.type = self.RECURRENT
        self.save()
        self.scheduled_dates.all().delete()

    def switch_to_scheduled(self):
        self.type = self.SCHEDULED
        self.save()
        self.recurring_alerts.all().delete()


class ScheduledWorkoutDate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime = models.DateTimeField()
    activated = models.BooleanField(default=False)

    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name="scheduled_dates"
    )

    def __str__(self):
        return f"{self.workout.name} - {self.datetime}"

    def activate(self):
        self.activated = True
        self.save()

    def save(self, *args, **kwargs):
        previous = ScheduledWorkoutDate.objects.filter(id=self.id).first()
        if previous and previous.datetime != self.datetime:
            self.activated = False

        return super().save(*args, **kwargs)


class RecurringWorkoutAlert(models.Model):
    WEEK_DAYS = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.TimeField()
    week_days = models.JSONField(
        default=list, blank=True
    )  # List of days of the week (0-6)
    activated = models.BooleanField(default=False)

    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name="recurring_alerts"
    )

    def __str__(self):
        return f"{self.workout.name} - {self.get_week_days_display()} {self.time}"

    def get_week_days_display(self):
        if not self.week_days:
            return "No set days"
        return ", ".join([dict(self.WEEK_DAYS).get(day, "") for day in self.week_days])

    def activate(self):
        self.activated = True
        self.save()


class WorkoutComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField()

    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name="comments"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} ({self.workout.name})"
