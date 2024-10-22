from rest_framework import serializers

from . import models


class ExerciseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExerciseCategory
        fields = "__all__"


class ExerciseSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = models.Exercise
        fields = "__all__"

    def get_category(self, instance):
        return str(instance.category)


class ExercisePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExercisePlan
        fields = "__all__"
        read_only_fields = ["workout", "created_at", "updated_at"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["exercise"] = ExerciseSerializer(instance.exercise).data
        return repr

    def create(self, validated_data):
        validated_data["workout"] = self.context["workout"]
        return super().create(validated_data)


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workout
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkoutComment
        fields = "__all__"
        read_only_fields = ["workout", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["workout"] = self.context["workout"]
        return super().create(validated_data)
