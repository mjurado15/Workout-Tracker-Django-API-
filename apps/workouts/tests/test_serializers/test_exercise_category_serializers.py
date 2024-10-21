import uuid

import pytest
from django_mock_queries.query import MockModel

from workouts.serializers import ExerciseCategorySerializer


pytestmark = [pytest.mark.unit]


class TestExerciseCategorySerializer:
    def test_serialize_model(self):
        category_data = {
            "id": uuid.uuid4(),
            "name": "Cardio",
        }
        category = MockModel(**category_data)
        serializer = ExerciseCategorySerializer(category)

        expected_data = {**category_data, "id": str(category_data["id"])}

        assert serializer.data == expected_data

    def test_valid_data(self):
        category_data = {"name": "Cardio"}
        serializer = ExerciseCategorySerializer(data=category_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data.keys()) == set(category_data.keys())

    def test_invalid_data(self):
        category_data = {}
        serializer = ExerciseCategorySerializer(data=category_data)

        assert not serializer.is_valid()
        assert serializer.errors != {}

    def test_ignore_extra_fields(self):
        category_data = {
            "name": "Cardio",
            "extra_field": "extra value",
        }
        serializer = ExerciseCategorySerializer(data=category_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data
