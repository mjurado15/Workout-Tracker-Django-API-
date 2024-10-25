from rest_framework import viewsets
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from workouts.models import ExercisePlan, Workout
from workouts.serializers import ExercisePlanSerializer


class ExercisePlanViews(viewsets.ModelViewSet):
    serializer_class = ExercisePlanSerializer

    def get_queryset(self):
        workout = get_object_or_404(
            Workout, pk=self.kwargs["workout_pk"], user=self.request.user
        )

        return ExercisePlan.objects.filter(workout=workout).order_by(
            Lower("name"), "-created_at"
        )

    def get_serializer_context(self):
        context = {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
        }

        if self.request.method == "POST":
            workout = get_object_or_404(
                Workout, pk=self.kwargs["workout_pk"], user=self.request.user
            )
            context["workout"] = workout

        return context
