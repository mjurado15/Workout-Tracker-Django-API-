from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from workouts.models import WorkoutComment, Workout
from workouts.serializers import CommentSerializer


class CommentViews(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        workout = get_object_or_404(
            Workout, pk=self.kwargs["workout_pk"], user=self.request.user
        )

        return WorkoutComment.objects.filter(workout=workout).order_by("-created_at")

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
