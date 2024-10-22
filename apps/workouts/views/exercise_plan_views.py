from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from workouts.models import ExercisePlan
from workouts.serializers import ExercisePlanSerializer


class ExercisePlanViews:
    @action(methods=["GET", "POST"], detail=True)
    def exercise_plans(self, request, *args, **kwargs):
        workout = self.get_object()
        exercise_plan_serializer = ExercisePlanSerializer

        if request.method == "GET":
            exercise_plans = workout.exercise_plans.all().order_by(
                Lower("name"), "-created_at"
            )
            queryset = self.filter_queryset(exercise_plans)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = exercise_plan_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = exercise_plan_serializer(queryset, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = exercise_plan_serializer(
                data=request.data, context={"workout": workout}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["GET", "PATCH", "DELETE"],
        detail=True,
        url_path="exercise_plans/(?P<exericise_plan_pk>[^/.]+)",
    )
    def exercise_plan_detail(self, request, *args, **kwargs):
        workout = self.get_object()
        exercise_plan = get_object_or_404(
            ExercisePlan, pk=kwargs.get("exericise_plan_pk"), workout=workout
        )
        exercise_plan_serializer = ExercisePlanSerializer

        if request.method == "GET":
            data = exercise_plan_serializer(exercise_plan).data
            return Response(data)

        if request.method == "PATCH":
            serializer = exercise_plan_serializer(
                exercise_plan, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == "DELETE":
            exercise_plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
