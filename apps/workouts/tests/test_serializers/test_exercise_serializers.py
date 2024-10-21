import uuid

import pytest
from django_mock_queries.query import MockModel

from workouts.serializers import ExerciseSerializer


pytestmark = [pytest.mark.unit]


class TestExerciseSerializer:
    def test_serialize_model(self):
        category_data = {"name": "Cardio"}
        mock_category = MockModel(**category_data)
        type(mock_category).__str__ = lambda self: category_data["name"]

        exercise_data = {
            "id": uuid.uuid4(),
            "name": "Running",
            "description": "Running description",
            "category": mock_category,
        }
        mock_exercise = MockModel(**exercise_data)

        serializer = ExerciseSerializer(mock_exercise)
        expected_data = {
            **exercise_data,
            "id": str(exercise_data["id"]),
            "category": category_data["name"],
        }

        assert serializer.data == expected_data

    def test_valid_data(self):
        exercise_data = {
            "name": "Running",
            "description": "Running description",
        }
        serializer = ExerciseSerializer(data=exercise_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == set(exercise_data.keys())

    def test_invalid_data(self):
        exercise_data = {}
        serializer = ExerciseSerializer(data=exercise_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_ignore_extra_fields(self):
        exercise_data = {
            "name": "Running",
            "description": "Running description",
            "extra_field": "extra value",
        }
        serializer = ExerciseSerializer(data=exercise_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data
