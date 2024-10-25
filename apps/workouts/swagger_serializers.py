from workouts import serializers


class ExercisePlanResponseSerializer(serializers.ExercisePlanSerializer):
    exercise = serializers.ExerciseSerializer()
