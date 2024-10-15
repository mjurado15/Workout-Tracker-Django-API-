import pytest
from django.core.exceptions import ValidationError

from apps.workouts.models import Exercise


pytestmark = [pytest.mark.django_db, pytest.mark.unit]


class TestExerciseModel:
    def test_create_exercise(self, exercise_built_with_category):
        exercise = Exercise.objects.create(**exercise_built_with_category)
        assert exercise.name == exercise_built_with_category["name"]
        assert exercise.category == exercise_built_with_category["category"]

    def test_create_exercise_with_description(self, exercise_built_with_category):
        exercise_built_with_category["description"] = "This is a test description"
        exercise = Exercise.objects.create(**exercise_built_with_category)
        assert exercise.name == exercise_built_with_category["name"]
        assert exercise.description == exercise_built_with_category["description"]

    @pytest.mark.parametrize(
        "field, empty_value",
        [
            ("name", ""),
            ("category", None),
        ],
    )
    def test_required_field_cannot_be_empty(
        self, field, empty_value, exercise_built_with_category
    ):
        exercise_built_with_category[field] = empty_value
        exercise = Exercise(**exercise_built_with_category)
        with pytest.raises(ValidationError):
            exercise.full_clean()

    def test_description_can_be_empty(self, exercise_built_with_category):
        exercise_built_with_category["description"] = ""
        exercise = Exercise(**exercise_built_with_category)
        exercise.full_clean()

    def test_max_length_name(self, exercise_built_with_category):
        exercise_built_with_category["name"] = "a" * 156
        exercise = Exercise(**exercise_built_with_category)
        with pytest.raises(ValidationError):
            exercise.full_clean()

    def test_category_cascade_delete(self, exercise_built_with_category):
        category = exercise_built_with_category["category"]
        exercise = Exercise.objects.create(**exercise_built_with_category)
        assert exercise in Exercise.objects.all()

        category.delete()
        assert exercise not in Exercise.objects.all()

    def test_category_related_name_exercises(self, exercise_built_with_category):
        category = exercise_built_with_category["category"]
        exercise = Exercise.objects.create(**exercise_built_with_category)
        assert category.exercises.count() == 1
        assert exercise in category.exercises.all()

    def test_str_representation(self, exercise_built_with_category):
        exercise = Exercise(**exercise_built_with_category)
        assert str(exercise) == exercise_built_with_category["name"]
