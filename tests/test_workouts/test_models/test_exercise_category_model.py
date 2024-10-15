import pytest
from django.core.exceptions import ValidationError

from apps.workouts.models import ExerciseCategory


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

    def test_max_length_name(self):
        category_name = "a" * 101
        exercise = ExerciseCategory(name=category_name)
        with pytest.raises(ValidationError):
            exercise.full_clean()

    def test_str_representation(self):
        category = ExerciseCategory.objects.create(name="flexibility")
        assert str(category) == "flexibility"
