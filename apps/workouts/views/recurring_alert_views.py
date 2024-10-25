from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, extend_schema_view

from workouts.models import RecurringWorkoutAlert, Workout
from workouts.serializers import RecurringAlertSerializer


@extend_schema_view(
    list=extend_schema(tags=["recurring workout alerts"]),
    create=extend_schema(tags=["recurring workout alerts"]),
    retrieve=extend_schema(tags=["recurring workout alerts"]),
    update=extend_schema(tags=["recurring workout alerts"]),
    partial_update=extend_schema(tags=["recurring workout alerts"]),
    destroy=extend_schema(tags=["recurring workout alerts"]),
)
class RecurringAlertViews(viewsets.ModelViewSet):
    serializer_class = RecurringAlertSerializer

    def get_queryset(self):
        workout = self.kwargs.get("workout") or get_object_or_404(
            Workout, pk=self.kwargs["workout_pk"], user=self.request.user
        )

        return RecurringWorkoutAlert.objects.filter(workout=workout).order_by("time")

    def get_serializer_context(self):
        context = {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
        }

        if self.request.method == "POST":
            context["workout"] = self.kwargs["workout"]

        return context

    def list(self, request, *args, **kwargs):
        workout = get_object_or_404(
            Workout, pk=self.kwargs["workout_pk"], user=self.request.user
        )
        self.kwargs["workout"] = workout

        if not workout.is_recurrent():
            return Response(
                {"detail": "The workout is not recurrent."},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        workout = get_object_or_404(
            Workout, pk=self.kwargs["workout_pk"], user=self.request.user
        )
        self.kwargs["workout"] = workout

        if not workout.is_recurrent():
            workout.switch_to_recurrent()

        return super().create(request, *args, **kwargs)
