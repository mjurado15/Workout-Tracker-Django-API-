import json
import pytest

from .factories import ExerciseCategoryFactory


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
