from django.db import models
from django.utils.translation import gettext_lazy as _


class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("exercise category")
        verbose_name_plural = _("exercise categories")

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
