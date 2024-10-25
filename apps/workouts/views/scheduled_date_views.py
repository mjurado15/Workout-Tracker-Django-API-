from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, extend_schema_view

from workouts.models import ScheduledWorkoutDate, Workout
from workouts.serializers import ScheduledDateSerializer


@extend_schema_view(
    list=extend_schema(tags=["scheduled workout dates"]),
    create=extend_schema(tags=["scheduled workout dates"]),
    retrieve=extend_schema(tags=["scheduled workout dates"]),
    update=extend_schema(tags=["scheduled workout dates"]),
    partial_update=extend_schema(tags=["scheduled workout dates"]),
    destroy=extend_schema(tags=["scheduled workout dates"]),
)
class ScheduledDateViews(viewsets.ModelViewSet):
    serializer_class = ScheduledDateSerializer

    def get_queryset(self):
        workout = self.kwargs.get("workout") or get_object_or_404(
            Workout, pk=self.kwargs["workout_pk"], user=self.request.user
        )

        return ScheduledWorkoutDate.objects.filter(workout=workout).order_by("datetime")

    def get_serializer_context(self):
        context = {"request": self.request, "format": self.format_kwarg, "view": self}

        if self.request.method == "POST":
            context["workout"] = self.kwargs["workout"]

        return context

    def list(self, request, *args, **kwargs):
        workout = get_object_or_404(
            Workout, pk=self.kwargs["workout_pk"], user=self.request.user
        )
        self.kwargs["workout"] = workout

        if not workout.is_scheduled():
            return Response(
                {"detail": "The workout is not scheduled."},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        workout = get_object_or_404(
            Workout, pk=self.kwargs["workout_pk"], user=self.request.user
        )
        self.kwargs["workout"] = workout

        if not workout.is_scheduled():
            workout.switch_to_scheduled()

        return super().create(request, *args, **kwargs)
