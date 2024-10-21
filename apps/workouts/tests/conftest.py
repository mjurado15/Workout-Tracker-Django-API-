import json
import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory

from .factories import ExerciseCategoryFactory, ExerciseFactory


@pytest.fixture
def seed_data():
    return {
        "exercise_categories": [
            {
                "name": "Cardio",
                "exercises": [
                    {
                        "name": "Running",
                        "description": "A high-intensity activity that improves cardiovascular endurance by running at a steady pace.",
                    }
                ],
            },
            {
                "name": "Flexibility",
                "exercises": [
                    {
                        "name": "Hamstring Stretch",
                        "description": "Hamstring Stretch description",
                    },
                    {
                        "name": "Cat-Cow Stretch",
                        "description": "Cat-Cow Stretch",
                    },
                ],
            },
        ]
    }


@pytest.fixture
def mock_open_seed_data(mocker, seed_data):
    mock_open = mocker.mock_open(read_data=json.dumps(seed_data))
    mocker.patch("builtins.open", mock_open)
    return mock_open


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_created():
    return UserFactory.create()


@pytest.fixture
def exercise_category_created():
    return ExerciseCategoryFactory.create()


@pytest.fixture
def create_exercise_category_with():
    def create_exercise_category(**kwargs):
        return ExerciseCategoryFactory.create(**kwargs)

    return create_exercise_category


@pytest.fixture
def create_batch_exercise_categories():
    def create_exercise_categories(size):
        return ExerciseCategoryFactory.create_batch(size)

    return create_exercise_categories


@pytest.fixture
def create_exercise_with():
    def create_exercise(**kwargs):
        return ExerciseFactory.create(**kwargs)

    return create_exercise


@pytest.fixture
def create_batch_exercises_with():
    def create_exercises(size, **kwargs):
        return ExerciseFactory.create_batch(size, **kwargs)

    return create_exercises
