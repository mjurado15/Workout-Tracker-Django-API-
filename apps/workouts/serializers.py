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
