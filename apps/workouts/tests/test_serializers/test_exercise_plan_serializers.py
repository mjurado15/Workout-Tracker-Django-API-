import uuid
from django.utils import timezone

import pytest
from django_mock_queries.query import MockModel, MockSet

from workouts.serializers import ExercisePlanSerializer
from workouts.tests.utils import serialize_datetime


pytestmark = [pytest.mark.unit]


class TestExercisePlanSerializer:
    def test_serialize_model(self, mocker):
        workout_data = {
            "id": uuid.uuid4(),
            "name": "Test Workout",
        }
        mock_workout = MockModel(**workout_data, pk=str(workout_data["id"]))

        exercise_data = {
            "id": uuid.uuid4(),
            "name": "Running",
            "description": "running description",
            "category": "Cardio",
        }
        mock_exercise = MockModel(**exercise_data)

        mock_exercise_serializer = mocker.patch(
            "workouts.serializers.ExerciseSerializer"
        )
        mock_exercise_serializer.return_value.data = {
            **exercise_data,
            "id": str(exercise_data["id"]),
        }

        plan_data = {
            "name": "Test exercise plan",
            "description": "Description",
            "sets": 4,
            "reps": 15,
            "weight": None,
            "weight_measure_unit": "",
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "exercise": mock_exercise,
            "workout": mock_workout,
        }
        mock_plan = MockModel(**plan_data)
        mock_plan.serializable_value = lambda field_name: getattr(mock_plan, field_name)

        serializer = ExercisePlanSerializer(mock_plan)

        expected_data = {
            **plan_data,
            "created_at": serialize_datetime(plan_data["created_at"]),
            "updated_at": serialize_datetime(plan_data["updated_at"]),
            "exercise": {**exercise_data, "id": str(exercise_data["id"])},
            "workout": str(workout_data["id"]),
        }
        assert serializer.data == expected_data

    def test_valid_data(self, mocker):
        exercise_id = uuid.uuid4()
        mock_exercise = MockModel(pk=str(exercise_id))
        mocker.patch(
            "workouts.models.Exercise.objects.all", return_value=MockSet(mock_exercise)
        )

        plan_data = {
            "name": "Test exercise plan",
            "description": "Description",
            "exercise": str(exercise_id),
        }
        serializer = ExercisePlanSerializer(data=plan_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == set(plan_data.keys())

    def test_invalid_data(self):
        plan_data = {}
        serializer = ExercisePlanSerializer(data=plan_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_ignore_extra_fields(self, mocker):
        exercise_id = uuid.uuid4()
        mock_exercise = MockModel(pk=str(exercise_id))
        mocker.patch(
            "workouts.models.Exercise.objects.all", return_value=MockSet(mock_exercise)
        )

        plan_data = {
            "name": "Running",
            "description": "Running description",
            "exercise": str(exercise_id),
            "extra_field": "extra value",
        }
        serializer = ExercisePlanSerializer(data=plan_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data

    def test_create_method_adds_the_workout(self, mocker):
        exercise_id = uuid.uuid4()
        mock_exercise = MockModel(pk=str(exercise_id))
        mocker.patch(
            "workouts.models.Exercise.objects.all", return_value=MockSet(mock_exercise)
        )

        mock_workout = MockModel(id=uuid.uuid4())
        plan_data = {
            "name": "Test exercise plan",
            "description": "Description",
            "exercise": str(exercise_id),
        }

        mock_model_create = mocker.patch(
            "workouts.serializers.serializers.ModelSerializer.create",
            return_value=MockModel(id=uuid.uuid4(), **plan_data, workout=mock_workout),
        )

        serializer = ExercisePlanSerializer(
            data=plan_data, context={"workout": mock_workout}
        )
        serializer.is_valid()

        plan_created = serializer.create(serializer.validated_data)

        mock_model_create.assert_called_once_with(
            {**serializer.validated_data, "workout": mock_workout}
        )
        assert plan_created.id is not None
        assert plan_created.name == plan_data["name"]
