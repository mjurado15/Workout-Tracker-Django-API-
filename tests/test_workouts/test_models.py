import pytest
from django.core.exceptions import ValidationError

from apps.workouts.models import ExerciseCategory, Exercise


pytestmark = [pytest.mark.django_db, pytest.mark.unit]


class TestExerciseCategoryModel:
    def test_create_exercise_category(self):
        category_name = "flexibility"
        category = ExerciseCategory.objects.create(name=category_name)

        assert category.id != None
        assert category.name == category_name

    def test_name_cannot_be_empty(self):
        category = ExerciseCategory(name="")
        with pytest.raises(ValidationError):
            category.full_clean()

    def test_str_representation(self):
        category = ExerciseCategory.objects.create(name="flexibility")
        assert str(category) == "flexibility"


class TestExercise:
    def test_create_exercise(self, exercise_built):
        exercise = Exercise.objects.create(**exercise_built)
        assert exercise.name == exercise_built["name"]
        assert exercise.category == exercise_built["category"]

    def test_create_exercise_with_description(self, exercise_built):
        exercise_built["description"] = "This is a test description"
        exercise = Exercise.objects.create(**exercise_built)
        assert exercise.name == exercise_built["name"]
        assert exercise.description == exercise_built["description"]

    @pytest.mark.parametrize(
        "field, empty_value",
        [
            ("name", ""),
            ("category", None),
        ],
    )
    def test_required_field_cannot_be_empty(self, field, empty_value, exercise_built):
        exercise_built[field] = empty_value
        exercise = Exercise(**exercise_built)
        with pytest.raises(ValidationError):
            exercise.full_clean()

    def test_description_can_be_empty(self, exercise_built):
        exercise_built["description"] = ""
        exercise = Exercise(**exercise_built)
        exercise.full_clean()

    def test_max_length_name(self, exercise_built):
        exercise_built["name"] = "a" * 156
        exercise = Exercise(**exercise_built)
        with pytest.raises(ValidationError):
            exercise.full_clean()

    def test_category_cascade_delete(self, exercise_built):
        category = exercise_built["category"]
        exercise = Exercise.objects.create(**exercise_built)
        assert exercise in Exercise.objects.all()

        category.delete()
        assert exercise not in Exercise.objects.all()

    def test_category_related_name_exercises(self, exercise_built):
        category = exercise_built["category"]
        exercise = Exercise.objects.create(**exercise_built)
        assert category.exercises.count() == 1
        assert exercise in category.exercises.all()

    def test_str_representation(self, exercise_built):
        exercise = Exercise(**exercise_built)
        assert str(exercise) == exercise_built["name"]
