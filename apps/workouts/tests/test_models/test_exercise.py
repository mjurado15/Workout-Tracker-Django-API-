import pytest

from workouts.models import Exercise


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestExerciseModel:
    def test_create_exercise(self, exercise_category_created):
        exercise_data = {
            "name": "Running",
            "category": exercise_category_created,
        }

        exercise = Exercise.objects.create(**exercise_data)

        assert exercise.id is not None
        assert all(
            [
                getattr(exercise, field) == exercise_data[field]
                for field in exercise_data
            ]
        )

    def test_exercise_str(self):
        exercise_data = {
            "name": "Running",
        }
        exercise = Exercise(**exercise_data)

        assert str(exercise) == exercise_data["name"]

    def test_default_description(self, exercise_category_created):
        exercise_data = {
            "name": "Running",
            "category": exercise_category_created,
        }

        exercise = Exercise.objects.create(**exercise_data)

        assert exercise.description == ""

    def test_create_exercise_with_optional_description(self, exercise_category_created):
        exercise_data = {
            "name": "Running",
            "category": exercise_category_created,
            "description": "Running description",
        }
        exercise = Exercise.objects.create(**exercise_data)

        assert exercise.description == exercise_data["description"]

    def test_exercise_category_cascade_delete(self, exercise_category_created):
        category = exercise_category_created
        exercise_data = {
            "name": "Running",
            "category": exercise_category_created,
        }
        Exercise.objects.create(**exercise_data)

        assert Exercise.objects.count() == 1
        category.delete()

        assert Exercise.objects.count() == 0

    def test_exercise_category_relationship(self, exercise_category_created):
        category = exercise_category_created
        exercise_data = {
            "name": "Running",
            "category": exercise_category_created,
        }

        exercise = Exercise.objects.create(**exercise_data)

        assert category.exercises.count() == 1
        assert category.exercises.first() == exercise
