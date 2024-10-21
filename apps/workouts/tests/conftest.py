import pytest

from .factories import ExerciseCategoryFactory


@pytest.fixture
def exercise_category_created():
    return ExerciseCategoryFactory.create()
