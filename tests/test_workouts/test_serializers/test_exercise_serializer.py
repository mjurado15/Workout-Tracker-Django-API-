import pytest
from django_mock_queries.query import MockModel, MockSet

from apps.workouts.serializers import ExerciseSerializer, NestedExerciseSerializer

pytestmark = [pytest.mark.unit]


class TestExerciseSerializer:
    def test_serialization(self):
        mock_category = MockModel(pk=1, name="Cardio")
        mock_category.serializable_value = lambda field_name: getattr(
            mock_category, field_name
        )

        mock_exercise = MockModel(
            id=1,
            name="Running",
            description="Running description",
            category=mock_category,
        )
        mock_exercise.serializable_value = lambda field_name: getattr(
            mock_exercise, field_name
        )

        serializer = ExerciseSerializer(mock_exercise)

        expected_data = {
            "id": 1,
            "name": "Running",
            "description": "Running description",
            "category": 1,
        }

        assert serializer.data == expected_data

    def test_valid_data(self, mocker):
        mock_category = MockModel(pk=2, name="Cardio")
        mocker.patch(
            "apps.workouts.models.ExerciseCategory.objects.all",
            return_value=MockSet(
                mock_category,
            ),
        )

        exercise_data = {
            "name": "Running",
            "description": "Running description",
            "category": 2,
        }
        serializer = ExerciseSerializer(data=exercise_data)

        assert serializer.is_valid()
        assert set(serializer.validated_data) == {"name", "description", "category"}

    def test_invalid_data_raises_error(self):
        exercise_data = {
            "name": "",
            "description": None,
            "category": None,
        }
        serializer = ExerciseSerializer(data=exercise_data)

        assert not serializer.is_valid()
        assert set(serializer.errors) == {"name", "description", "category"}

    def test_data_with_a_non_existent_category_raises_error(self, mocker):
        mocker.patch(
            "apps.workouts.models.ExerciseCategory.objects.all", return_value=MockSet()
        )

        exercise_data = {"name": "Running", "category": 2}
        serializer = ExerciseSerializer(data=exercise_data)

        assert not serializer.is_valid()
        assert (
            str(serializer.errors["category"][0])
            == 'Invalid pk "2" - object does not exist.'
        )

    def test_ignore_extra_fields(self, mocker):
        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value.exists.return_value = True
        mocker.patch(
            "apps.workouts.models.ExerciseCategory.objects.all",
            return_value=mock_queryset,
        )

        exercise_data = {
            "name": "Running",
            "description": "Running description",
            "category": 2,
            "extra_field": "Extra value",
        }

        serializer = ExerciseSerializer(data=exercise_data)

        assert serializer.is_valid()
        assert "extra_field" not in serializer.validated_data


class TestNestedExerciseSerializer:
    def test_serializer_model_with_category_str(self):
        mock_category = MockModel(pk=1, name="Cardio")
        type(mock_category).__str__ = lambda self: "Cardio"

        exercise_data = {
            "name": "Running",
            "description": "Running description",
            "category": mock_category,
        }
        mock_exercise = MockModel(**exercise_data)

        serializer = NestedExerciseSerializer(mock_exercise)

        expected_data = {
            **exercise_data,
            "category": "Cardio",
        }

        assert serializer.data == expected_data
