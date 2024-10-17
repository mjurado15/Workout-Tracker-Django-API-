from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from . import models, serializers


class ExerciseCategoryViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = models.ExerciseCategory.objects.all().order_by("name", "-id")
    serializer_class = serializers.ExerciseCategorySerializer


class ExerciseViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = models.Exercise.objects.all().order_by(
        Lower("name"), Lower("category__name"), "-id"
    )
    serializer_class = serializers.ExerciseSerializer


class WorkoutPlanViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.WorkoutPlanSerializer

    def get_queryset(self):
        return models.WorkoutPlan.objects.filter(user=self.request.user).order_by(
            "-created_at", "-id"
        )

    @action(methods=["POST"], detail=True)
    def change_of_status(self, request, *args, **kwargs):
        workout_instance = self.get_object()

        serializer = serializers.WorkoutPlanStatusSerializer(
            workout_instance, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=["GET", "POST"], detail=True)
    def exercise_plans(self, request, *args, **kwargs):
        workout_instance = self.get_object()

        if request.method == "GET":
            exercise_plans = workout_instance.exercise_plans.all().order_by("-id")

            page = self.paginate_queryset(exercise_plans)
            if page is not None:
                serializer = serializers.ExercisePlanSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = serializers.ExercisePlanSerializer(exercise_plans, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = serializers.ExercisePlanSerializer(
                data=request.data, context={"workout_plan": workout_instance}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["GET", "PUT", "PATCH", "DELETE"],
        detail=True,
        url_path="exercise_plans/(?P<exercise_pk>[^/.]+)",
    )
    def exercise_plan_detail(self, request, *args, **kwargs):
        workout_instance = self.get_object()
        exercise_plan = get_object_or_404(
            models.ExercisePlan,
            pk=kwargs.get("exercise_pk"),
            workout_plan=workout_instance,
        )

        if request.method == "GET":
            serializer = serializers.ExercisePlanSerializer(exercise_plan)
            return Response(serializer.data)

        if request.method == "PUT":
            serializer = serializers.ExercisePlanSerializer(
                exercise_plan, data=request.data, partial=False
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == "PATCH":
            serializer = serializers.ExercisePlanSerializer(
                exercise_plan, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == "DELETE":
            exercise_plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET", "POST"], detail=True)
    def comments(self, request, *args, **kwargs):
        workout_instance = self.get_object()

        if request.method == "GET":
            comments = workout_instance.comments.all().order_by("-created_at", "-id")

            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = serializers.WorkoutCommentSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = serializers.WorkoutCommentSerializer(comments, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = serializers.WorkoutCommentSerializer(
                data=request.data, context={"workout_plan": workout_instance}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["GET", "PUT", "DELETE"],
        detail=True,
        url_path="comments/(?P<comment_pk>[^/.]+)",
    )
    def comment_detail(self, request, *args, **kwargs):
        workout_instance = self.get_object()
        comment = get_object_or_404(
            models.WorkoutComment,
            pk=kwargs.get("comment_pk"),
            workout_plan=workout_instance,
        )

        if request.method == "GET":
            serializer = serializers.WorkoutCommentSerializer(comment)
            return Response(serializer.data)

        if request.method == "PUT":
            serializer = serializers.WorkoutCommentSerializer(
                comment, data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == "DELETE":
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
