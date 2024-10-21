import pytest

from workouts.models import ExerciseCategory


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestExerciseCategory:
    def test_create_exercise_category(self):
        category_data = {
            "name": "Cardio",
        }

        category = ExerciseCategory.objects.create(**category_data)

        assert category.id is not None
        assert category.name == category_data["name"]

    def test_exercise_category_str(self):
        category_data = {
            "name": "Cardio",
        }
        category = ExerciseCategory(**category_data)

        assert str(category.name) == category_data["name"]
