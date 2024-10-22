import json
import pytest

from .factories import (
    ExerciseCategoryFactory,
    ExerciseFactory,
    WorkoutFactory,
    ExercisePlanFactory,
    WorkoutCommentFactory,
)


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
def exercise_created():
    return ExerciseFactory.create()


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


@pytest.fixture
def workout_created():
    return WorkoutFactory.create()


@pytest.fixture
def create_workout_with():
    def create_workout(**kwargs):
        return WorkoutFactory.create(**kwargs)

    return create_workout


@pytest.fixture
def create_batch_workouts_with():
    def create_workouts_with(size, **kwargs):
        return WorkoutFactory.create_batch(size, **kwargs)

    return create_workouts_with


@pytest.fixture
def exercise_plan_created():
    return ExercisePlanFactory.create()


@pytest.fixture
def create_exercise_plan_with():
    def create_exercise_plan_with(**kwargs):
        return ExercisePlanFactory.create(**kwargs)

    return create_exercise_plan_with


@pytest.fixture
def create_batch_exercise_plans_with():
    def create_batch_with(size, **kwargs):
        return ExercisePlanFactory.create_batch(size, **kwargs)

    return create_batch_with


@pytest.fixture
def comment_created():
    return WorkoutCommentFactory.create()


@pytest.fixture
def create_comment_with():
    def comment_with(**kwargs):
        return WorkoutCommentFactory.create(**kwargs)

    return comment_with


@pytest.fixture
def create_batch_comments_with():
    def create_batch_with(size, **kwargs):
        return WorkoutCommentFactory.create_batch(size, **kwargs)

    return create_batch_with
