import json
import pytest

from tests.test_users.factories import UserFactory
from .factories import ExerciseFactory, ExerciseCategoryFactory, WorkoutPlanFactory


@pytest.fixture
def mock_open_seed_data(mocker, cardio_exercise_category):
    mock_open = mocker.mock_open(
        read_data=json.dumps(
            {
                "exercise_categories": [
                    cardio_exercise_category,
                ]
            }
        )
    )
    mocker.patch("builtins.open", mock_open)
    return mock_open


@pytest.fixture
def create_batch_exercise_categories():
    def create_exercise_categories(size: int):
        return ExerciseCategoryFactory.create_batch(size)

    return create_exercise_categories


@pytest.fixture
def exercise_category_created():
    return ExerciseCategoryFactory.create()


@pytest.fixture
def flexibility_exercise_category():
    return {
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
    }


@pytest.fixture
def cardio_exercise_category():
    return {
        "name": "Cardio",
        "exercises": [
            {
                "name": "Running",
                "description": "Running description",
            }
        ],
    }


@pytest.fixture
def exercise_built_with_category():
    exercise_built = ExerciseFactory.build(create_category=True)
    return {
        "name": exercise_built.name,
        "category": exercise_built.category,
    }


@pytest.fixture
def create_batch_exercises():
    def create_exercises(size: int):
        return ExerciseFactory.create_batch(size)

    return create_exercises


@pytest.fixture
def exercise_created():
    return ExerciseFactory.create()


@pytest.fixture
def user_created():
    return UserFactory.create()


@pytest.fixture
def create_batch_users():
    def create_users(size):
        return UserFactory.create_batch(size)

    return create_users


@pytest.fixture
def create_batch_workout_plans_with():
    def create_workout_plans(size, **kwargs):
        return WorkoutPlanFactory.create_batch(size, **kwargs)

    return create_workout_plans


@pytest.fixture
def workout_plan_created():
    return WorkoutPlanFactory.create()


@pytest.fixture
def workout_plan_built():
    return WorkoutPlanFactory.build()


@pytest.fixture
def exercise_plan_built(workout_plan_created):
    return {
        "name": "Test Exercise Plan",
        "description": "Test description",
        "workout_plan": workout_plan_created,
    }
