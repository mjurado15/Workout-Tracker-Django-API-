from rest_framework import mixins, viewsets
from django.db.models.functions import Lower

from . import models, serializers


class ExerciseCategoryViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = models.ExerciseCategory.objects.all().order_by("name", "id")
    serializer_class = serializers.ExerciseCategorySerializer


class ExerciseViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = models.Exercise.objects.all().order_by(
        Lower("name"), Lower("category__name"), "id"
    )
    serializer_class = serializers.ExerciseSerializer
