from rest_framework import viewsets
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema_view, extend_schema

from workouts import swagger_serializers
from workouts.models import ExercisePlan, Workout
from workouts.serializers import ExercisePlanSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["workout exercise plans"],
        responses={200: swagger_serializers.ExercisePlanResponseSerializer},
    ),
    create=extend_schema(
        tags=["workout exercise plans"],
        responses={201: swagger_serializers.ExercisePlanResponseSerializer},
    ),
    retrieve=extend_schema(
        tags=["workout exercise plans"],
        responses={200: swagger_serializers.ExercisePlanResponseSerializer},
    ),
    update=extend_schema(
        tags=["workout exercise plans"],
        responses={200: swagger_serializers.ExercisePlanResponseSerializer},
    ),
    partial_update=extend_schema(
        tags=["workout exercise plans"],
        responses={200: swagger_serializers.ExercisePlanResponseSerializer},
    ),
    destroy=extend_schema(tags=["workout exercise plans"]),
)
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
