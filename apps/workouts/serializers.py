from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from . import models


class ExerciseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExerciseCategory
        fields = "__all__"


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exercise
        fields = "__all__"


class NestedExerciseSerializer(ExerciseSerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, instance):
        return str(instance.category)


class ExercisePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExercisePlan
        exclude = ["workout_plan", "updated_at"]
        read_only_fields = ["is_completed"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["exercise"] = NestedExerciseSerializer(instance.exercise).data
        return representation

    def create(self, validated_data):
        validated_data["workout_plan"] = self.context["workout_plan"]
        return super().create(validated_data)


class WorkoutPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkoutPlan
        exclude = ["user", "updated_at"]
        read_only_fields = [
            "status",
            "is_completed",
            "started_at",
            "finished_at",
            "created_at",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class WorkoutPlanStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkoutPlan
        fields = [
            "id",
            "status",
            "started_at",
            "finished_at",
        ]
        read_only_fields = [
            "started_at",
            "finished_at",
        ]
        extra_kwargs = {
            "status": {"required": True},
        }

    def validate_status(self, value):
        if self.instance is not None:
            if value == "finished" and self.instance.status == "pending":
                raise ValidationError(
                    "The status cannot change directly from pending to finished"
                )
            if value == "pending" and self.instance.status == "finished":
                raise ValidationError(
                    "The status cannot change from finished to pending"
                )

        return value

    def create(self, validated_data):
        raise NotImplementedError("`create()` must be implemented.")


class WorkoutCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkoutComment
        fields = "__all__"
        read_only_fields = ["workout_plan", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["workout_plan"] = self.context["workout_plan"]
        return super().create(validated_data)
