import pytest
from django_mock_queries.query import MockModel

from apps.workouts.serializers import ExerciseCategorySerializer, ExerciseSerializer

pytestmark = [pytest.mark.unit]


class TestExerciseCategorySerializer:
    def test_serialization_successful(self):
        category = MockModel(id=1, name="Cardio")
        serializer = ExerciseCategorySerializer(category)

        assert serializer.data == {
            "id": 1,
            "name": "Cardio",
        }

    def test_serialization_with_invalid_model_raises_error(self):
        category = MockModel()
        serializer = ExerciseCategorySerializer(category)

        with pytest.raises(KeyError):
            serializer.data

    def test_valid_data(self):
        category_data = {"name": "Cardio"}
        serializer = ExerciseCategorySerializer(data=category_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == {"name"}

    def test_invalid_data(self):
        category_data = {}
        serializer = ExerciseCategorySerializer(data=category_data)

        assert not serializer.is_valid()
        assert set(serializer.errors) == {"name"}

    def test_ignore_extra_fields(self):
        category_data = {
            "name": "Cardio",
            "extra_field": "Extra value",
        }
        serializer = ExerciseCategorySerializer(data=category_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data
