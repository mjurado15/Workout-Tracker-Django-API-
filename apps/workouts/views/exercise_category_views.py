from django.db.models.functions import Lower
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema_view, extend_schema

from workouts import models, serializers


@extend_schema_view(
    list=extend_schema(tags=["exercise categories"]),
    exercises=extend_schema(tags=["exercise categories"]),
)
class ExerciseCategoryViews(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = models.ExerciseCategory.objects.all().order_by(Lower("name"))
    serializer_class = serializers.ExerciseCategorySerializer

    @extend_schema(responses={200: serializers.ExerciseSerializer(many=True)})
    @action(methods=["GET"], detail=True)
    def exercises(self, request, *args, **kwargs):
        category = self.get_object()
        exercises = category.exercises.all().order_by(Lower("name"))
        exercise_serializer = serializers.ExerciseSerializer

        page = self.paginate_queryset(exercises)
        if page is not None:
            serializer = exercise_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = exercise_serializer(exercises, many=True)
        return Response(serializer.data)
