from rest_framework import serializers

from . import models


class ExerciseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExerciseCategory
        fields = "__all__"


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exercise
        fields = "__all__"

    def to_representation(self, instance):
        return super().to_representation(instance)


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
