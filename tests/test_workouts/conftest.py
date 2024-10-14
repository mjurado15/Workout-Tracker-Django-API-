import json
import pytest

from .factories import ExerciseFactory


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
def exercise_built():
    exercise_built = ExerciseFactory.build(create_category=True)
    return {
        "name": exercise_built.name,
        "category": exercise_built.category,
    }
