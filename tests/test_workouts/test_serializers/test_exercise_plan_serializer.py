import pytest
from django.utils import timezone
from django_mock_queries.query import MockModel

from apps.workouts.serializers import ExercisePlanSerializer


pytestmark = [pytest.mark.unit]


class TestExercisePlanSerializer:
    def test_serialize_model(self):
        exercise_data = {
            "id": 1,
            "name": "Test Exercise Plan",
            "description": "Test description",
            "sets": 4,
            "reps": 15,
            "weight": 60,
            "weight_measure_unit": "pound",
            "is_completed": True,
            "created_at": timezone.now(),
        }
        exercise_plan = MockModel(**exercise_data)
        serializer = ExercisePlanSerializer(exercise_plan)

        expected_data = {
            **exercise_data,
            "created_at": exercise_data["created_at"].isoformat()[:-6] + "Z",
        }

        assert serializer.data == expected_data

    def test_valid_data(self, exercise_plan_built):
        exercise_plan_dict = exercise_plan_built.__dict__
        exercise_plan_dict.pop("id")
        exercise_plan_dict.pop("workout_plan_id")
        exercise_plan_dict.pop("_state")
        exercise_plan_dict.pop("is_completed")
        exercise_plan_dict.pop("created_at")
        exercise_plan_dict.pop("updated_at")

        serializer = ExercisePlanSerializer(data=exercise_plan_dict)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == set(exercise_plan_dict.keys())

    def test_invalid_data(self):
        exercise_plan_dict = {}
        serializer = ExercisePlanSerializer(data=exercise_plan_dict)

        assert not serializer.is_valid()
        assert set(serializer.errors) == {"name"}

    def test_ignore_extra_fields(self):
        exercise_plan_dict = {
            "name": "Test Exercise Plan",
            "extra_field": "extra value",
        }
        serializer = ExercisePlanSerializer(data=exercise_plan_dict)

        assert serializer.is_valid()
        assert "extra field" not in serializer.validated_data

    def test_create_method_adds_the_workout_plan(self, mocker):
        exercise_plan_dict = {
            "name": "Test Exercise Plan",
            "description": "Test Description",
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
