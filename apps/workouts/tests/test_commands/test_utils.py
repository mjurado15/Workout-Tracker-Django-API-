import pytest
from django_mock_queries.query import MockModel

from workouts.management.commands.populate_exercises import (
    remove_duplicate_items_by_name,
    remove_duplicate_exercises_by_name_and_category,
)


pytestmark = [pytest.mark.unit]


class TestRemoveDuplicatedItemsByName:
    def test_return_first_ocurrence_of_each_name(self):
        data = [
            {"name": "test 1", "description": "test 1 description (first)"},
            {"name": "test 2", "description": "test 2 description (first)"},
            {"name": "test 2", "description": "test 2 description (duplicated)"},
            {"name": "test 3", "description": "test 3 description"},
            {"name": "test 1", "description": "test 1 description (duplicated)"},
        ]
        result = remove_duplicate_items_by_name(data)

        assert result == [
            {"name": "test 1", "description": "test 1 description (first)"},
            {"name": "test 2", "description": "test 2 description (first)"},
            {"name": "test 3", "description": "test 3 description"},
        ]

    def test_empty_data_return_empty_list(self):
        result = remove_duplicate_items_by_name([])
        assert result == []

    def test_items_without_name_are_excluded(self):
        data = [
            {"description": "test 1 description (first)"},
            {"name": "test 2", "description": "test 2 description (first)"},
            {"name": "test 2", "description": "test 2 description (duplicated)"},
        ]
        result = remove_duplicate_items_by_name(data)

        assert result == [
            {"name": "test 2", "description": "test 2 description (first)"},
        ]


class TestRemoveDuplicateExercisesByNameCategory:
    def test_return_first_ocurrence_of_the_name_and_category_pair(self):
        cardio_category = MockModel(name="Cardio")
        flexibility_category = MockModel(name="Flexibility")

        exercise_one = MockModel(name="Running", category=cardio_category)
        exercise_two = MockModel(
            name="Hamstring Stretch", category=flexibility_category
        )
        exercise_one_duplicate = MockModel(name="Running", category=cardio_category)
        exercise_three = MockModel(name="Running", category=flexibility_category)

        result = remove_duplicate_exercises_by_name_and_category(
            [exercise_one, exercise_two, exercise_one_duplicate, exercise_three]
        )

        assert result == [exercise_one, exercise_two, exercise_three]

    @pytest.mark.parametrize(
        "name, category",
        [
            (None, MockModel(name="Cardio")),
            ("Test Exercise", None),
            (None, None),
        ],
    )
    def test_exercises_without_name_or_category_or_both_are_excluded(
        self, name, category
    ):
        cardio_category = MockModel(name="Cardio")
        flexibility_category = MockModel(name="Flexibility")
        exercise1 = MockModel(name="Running", category=cardio_category)
        exercise2 = MockModel(name=name, category=category)
        exercise3 = MockModel(name="Hamstring Stretch", category=flexibility_category)

        result = remove_duplicate_exercises_by_name_and_category(
            [exercise1, exercise2, exercise3]
        )

        assert result == [exercise1, exercise3]

    def test_emtpy_data_return_empty_list(self):
        result = remove_duplicate_exercises_by_name_and_category([])
        assert result == []
