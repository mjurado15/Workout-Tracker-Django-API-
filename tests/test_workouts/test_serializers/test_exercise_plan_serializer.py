import pytest
from django.utils import timezone
from django_mock_queries.query import MockModel, MockSet

from apps.workouts.serializers import ExercisePlanSerializer


pytestmark = [pytest.mark.unit]


class TestExercisePlanSerializer:
    def test_serialize_model(self, mocker):
        # Mock the related exercise
        exercise_data = {
            "id": 10,
            "name": "running",
            "description": "running description",
            "category": 2,
        }
        mock_exercise = MockModel(**exercise_data, pk=exercise_data["id"])
        mock_exercise.serializable_value = lambda field_name: getattr(
            mock_exercise, field_name
        )

        # Mock the nested exercise serializer
        mock_nested_serializer = mocker.patch(
            "apps.workouts.serializers.NestedExerciseSerializer",
        )
        mock_nested_serializer.return_value.data = {
            **exercise_data,
            "category": "Cardio",
        }

        # Mock the exercise plan instance
        exercise_plan_data = {
            "id": 1,
            "name": "Test Exercise Plan",
            "description": "Test description",
            "sets": 4,
            "reps": 15,
            "weight": 60,
            "weight_measure_unit": "pound",
            "is_completed": True,
            "created_at": timezone.now(),
            "exercise": mock_exercise,
        }
        mock_exercise_plan = MockModel(**exercise_plan_data)
        mock_exercise_plan.serializable_value = lambda field_name: getattr(
            mock_exercise_plan, field_name
        )

        # Serialize the exercise plan instance
        serializer = ExercisePlanSerializer(mock_exercise_plan)

        expected_data = {
            **exercise_plan_data,
            "created_at": exercise_plan_data["created_at"].isoformat()[:-6] + "Z",
            "exercise": {
                **exercise_data,
                "category": "Cardio",
            },
        }

        assert serializer.data == expected_data
        mock_nested_serializer.assert_called_once_with(mock_exercise)

    def test_valid_data(self, mocker):
        # Mock the related exercise
        mock_exercise = MockModel(pk=10, name="Cardio")
        mocker.patch(
            "apps.workouts.models.Exercise.objects.all",
            return_value=MockSet(mock_exercise),
        )

        exercise_plan_data = {
            "name": "Running",
            "description": "Running description",
            "exercise": 10,
        }
        serializer = ExercisePlanSerializer(data=exercise_plan_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == set(exercise_plan_data.keys())

    def test_invalid_data(self):
        exercise_plan_dict = {}
        serializer = ExercisePlanSerializer(data=exercise_plan_dict)

        assert not serializer.is_valid()
        assert set(serializer.errors) == {"name", "exercise"}

    def test_ignore_extra_fields(self, mocker):
        # Mock the related exercise
        mock_exercise = MockModel(pk=10, name="Cardio")
        mocker.patch(
            "apps.workouts.models.Exercise.objects.all",
            return_value=MockSet(mock_exercise),
        )

        exercise_plan_dict = {
            "name": "Test Exercise Plan",
            "exercise": 10,
            "extra_field": "extra value",
        }
        serializer = ExercisePlanSerializer(data=exercise_plan_dict)

        assert serializer.is_valid()
        assert "extra field" not in serializer.validated_data

    def test_create_method_adds_the_workout_plan(self, mocker):
        # Mock the related exercise
        mock_exercise = MockModel(pk=10, name="Cardio")
        mocker.patch(
            "apps.workouts.models.Exercise.objects.all",
            return_value=MockSet(mock_exercise),
        )

        exercise_plan_dict = {
            "name": "Test Exercise Plan",
            "description": "Test Description",
            "exercise": 10,
        }

        mock_workout_plan = MockModel(id=1, name="Workout Plan")
        mock_create = mocker.patch(
            "apps.workouts.serializers.serializers.ModelSerializer.create",
            return_value=MockModel(
                id=1, workout_plan=mock_workout_plan, **exercise_plan_dict
            ),
        )

        serializer = ExercisePlanSerializer(
            data=exercise_plan_dict, context={"workout_plan": mock_workout_plan}
        )

        serializer.is_valid()
        instance = serializer.create(serializer.validated_data)

        # assert instance.id == 1
        mock_create.assert_called_once_with(
            {**serializer.validated_data, "workout_plan": mock_workout_plan}
        )
        assert instance.id == 1
        assert instance.name == exercise_plan_dict["name"]
        assert instance.workout_plan == mock_workout_plan
