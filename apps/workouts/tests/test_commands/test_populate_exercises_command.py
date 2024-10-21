import os

import pytest
from unittest.mock import call
from django.conf import settings
from django_mock_queries.query import MockSet, MockModel

from workouts.management.commands.populate_exercises import (
    Command as PopulateExercisesCommand,
)
from workouts.models import ExerciseCategory, Exercise


pytestmark = [pytest.mark.unit]


class TestPopulateExercisesCommand:
    def test_handle(self, mocker, mock_open_seed_data, seed_data):
        exercise_categories_data = seed_data["exercise_categories"]

        mock_insert_exercise_categories = mocker.patch.object(
            PopulateExercisesCommand, "insert_exercise_categories"
        )
        mock_insert_exercises = mocker.patch.object(
            PopulateExercisesCommand, "insert_exercises"
        )
        command = PopulateExercisesCommand()
        mock_stdout_write = mocker.patch.object(command.stdout, "write")

        command.handle()

        mock_open_seed_data.assert_called_once_with(
            os.path.join(
                settings.BASE_DIR, "apps", "workouts", "data", "seed_data.json"
            ),
            "r",
        )
        mock_insert_exercise_categories.assert_called_once_with(
            [{"name": category["name"]} for category in exercise_categories_data]
        )
        mock_insert_exercises.assert_called_once_with(exercise_categories_data)
        mock_stdout_write.assert_called_once_with("Exercises added successfully!")

    def test_insert_exercise_categories__duplicate_categories_are_removed(self, mocker):
        mock_remove_duplicated = mocker.patch(
            "workouts.management.commands.populate_exercises.remove_duplicate_items_by_name"
        )
        mocker.patch("workouts.management.commands.populate_exercises.ExerciseCategory")

        categories_to_add = [{"name": "Cardio"}]

        command = PopulateExercisesCommand()
        command.insert_exercise_categories(categories_to_add)

        mock_remove_duplicated.assert_called_once_with(categories_to_add)

    def test_insert_exercise_categories__add_only_categories_that_do_not_exist(
        self, mocker
    ):
        mock_exercise_category = mocker.patch(
            "workouts.management.commands.populate_exercises.ExerciseCategory"
        )
        mock_exercise_category.objects.filter.return_value = MockSet(
            MockModel(name="Cardio")
        )
        command = PopulateExercisesCommand()
        mock_stdout_write = mocker.patch.object(command.stdout, "write")

        categories_to_add = [
            {"name": "Cardio"},
            {"name": "Strength"},
            {"name": "flexibility"},
        ]
        command.insert_exercise_categories(categories_to_add)

        mock_exercise_category.objects.bulk_create.assert_called_once_with(
            [
                mock_exercise_category(name="Strength"),
                mock_exercise_category(name="flexibility"),
            ]
        )
        mock_stdout_write.assert_called_once_with(
            "Successfully added 2 new exercise categories."
        )

    def test_insert_exercise_categories__all_already_exist(self, mocker):
        mock_exercise_category_objects = mocker.patch.object(
            ExerciseCategory, "objects"
        )
        mock_exercise_category_objects.filter.return_value = MockSet(
            MockModel(name="Cardio"), MockModel(name="Strength")
        )
        categories_to_add = [{"name": "Cardio"}, {"name": "Strength"}]
        command = PopulateExercisesCommand()
        mock_stdout_write = mocker.patch.object(command.stdout, "write")

        command.insert_exercise_categories(categories_to_add)

        mock_exercise_category_objects.bulk_create.assert_not_called()
        mock_stdout_write.assert_called_once_with("No new exercise categories to add.")

    def test_insert_exercise_categories__empty_list(self, mocker):
        mock_exercise_category_objects = mocker.patch.object(
            ExerciseCategory, "objects"
        )
        mock_exercise_category_objects.filter.return_value = MockSet()
        categories_to_add = []
        command = PopulateExercisesCommand()
        mock_stdout_write = mocker.patch.object(command.stdout, "write")

        command.insert_exercise_categories(categories_to_add)

        mock_exercise_category_objects.bulk_create.assert_not_called()
        mock_stdout_write.assert_called_once_with("No new exercise categories to add.")

    def test_insert_exercises__categories_that_do_not_exist_are_ignored(
        self, mocker, seed_data
    ):
        exercise_categories_data = seed_data["exercise_categories"]
        first_category = exercise_categories_data[0]
        second_category = exercise_categories_data[1]

        mock_exercise_category = mocker.patch(
            "workouts.management.commands.populate_exercises.ExerciseCategory"
        )
        mock_exercise = mocker.patch(
            "workouts.management.commands.populate_exercises.Exercise"
        )
        mocker.patch(
            "workouts.management.commands.populate_exercises.remove_duplicate_exercises_by_name_and_category"
        )
        #  Definir DoesNotExist como una excepción dentro del mock
        mock_exercise_category.DoesNotExist = type("DoesNotExist", (Exception,), {})

        mock_first_category = MockModel(name=first_category["name"])
        mock_second_category = MockModel(name=second_category["name"])

        mock_exercise_category.objects.get.side_effect = [
            mock_exercise_category.DoesNotExist("first error"),
            mock_first_category,
            mock_second_category,
        ]
        data_to_insert = [
            {
                "name": "Not exist",
                "exercises": [
                    {"name": "Exercise", "description": "Exercise description"},
                ],
            },
            first_category,
            second_category,
        ]

        command = PopulateExercisesCommand()
        command.insert_exercises(data_to_insert)

        assert mock_exercise.objects.filter.call_count == 2
        assert mock_exercise.objects.filter.call_args_list == [
            call(
                name__in=[item["name"] for item in first_category["exercises"]],
                category=mock_first_category,
            ),
            call(
                name__in=[item["name"] for item in second_category["exercises"]],
                category=mock_second_category,
            ),
        ]

    def test_insert_exercises__add_only_exercises_that_do_not_exist(
        self, mocker, seed_data
    ):
        exercise_categories_data = seed_data["exercise_categories"]
        first_category = exercise_categories_data[0]
        second_category = exercise_categories_data[1]

        mock_exercise_category = mocker.patch(
            "workouts.management.commands.populate_exercises.ExerciseCategory"
        )
        mock_exercise = mocker.patch(
            "workouts.management.commands.populate_exercises.Exercise"
        )
        mock_remove_duplicated_exercises = mocker.patch(
            "workouts.management.commands.populate_exercises.remove_duplicate_exercises_by_name_and_category"
        )

        input_data = [first_category, second_category]
        mock_first_category = MockModel(name=first_category["name"])
        mock_second_category = MockModel(name=second_category["name"])

        mock_exercise_category.objects.get.side_effect = [
            mock_first_category,
            mock_second_category,
        ]
        mock_exercise.objects.filter.side_effect = [
            MockSet(),
            MockSet(MockModel(**second_category["exercises"][0])),
        ]

        exercises_to_add_expected = [
            mock_exercise(**item, category=mock_first_category)
            for item in first_category["exercises"]
        ] + [
            mock_exercise(**item, category=mock_second_category)
            for item in second_category["exercises"][1::]
        ]

        mock_remove_duplicated_exercises.return_value = exercises_to_add_expected

        command = PopulateExercisesCommand()
        mock_stdout_write = mocker.patch.object(command.stdout, "write")

        command.insert_exercises(input_data)

        mock_remove_duplicated_exercises.assert_called_once_with(
            exercises_to_add_expected
        )
        mock_exercise.objects.bulk_create.assert_called_once_with(
            exercises_to_add_expected
        )
        mock_stdout_write.assert_called_once_with("Successfully added 2 new exercises.")

    def test_insert_exercises__all_already_exist(self, mocker, seed_data):
        exercise_categories_data = seed_data["exercise_categories"]
        category_data = exercise_categories_data[0]

        mock_exercise_category = mocker.patch(
            "workouts.management.commands.populate_exercises.ExerciseCategory"
        )
        mock_exercise_objects = mocker.patch.object(Exercise, "objects")
        mock_remove_duplicated_exercises = mocker.patch(
            "workouts.management.commands.populate_exercises.remove_duplicate_exercises_by_name_and_category"
        )

        input_data = [category_data]
        mock_category = mock_exercise_category(name=category_data["name"])

        mock_exercise_category.objects.get.return_value = mock_category

        mock_exercise_objects.filter.return_value = MockSet(
            *[
                MockModel(**item, category=mock_category)
                for item in category_data["exercises"]
            ]
        )

        mock_remove_duplicated_exercises.return_value = []

        command = PopulateExercisesCommand()
        mock_stdout_write = mocker.patch.object(command.stdout, "write")

        command.insert_exercises(input_data)

        mock_remove_duplicated_exercises.assert_called_once_with([])
        mock_exercise_objects.bulk_create.assert_not_called()
        mock_stdout_write.assert_called_once_with("No new exercises to add.")

    def test_insert_exercises__empty_list(self, mocker):
        mock_exercise_category_objects = mocker.patch.object(
            ExerciseCategory, "objects"
        )
        mock_exercise_objects = mocker.patch.object(Exercise, "objects")
        mock_remove_duplicated_exercises = mocker.patch(
            "workouts.management.commands.populate_exercises.remove_duplicate_exercises_by_name_and_category"
        )

        input_data = []
        mock_remove_duplicated_exercises.return_value = []

        command = PopulateExercisesCommand()
        mock_stdout_write = mocker.patch.object(command.stdout, "write")
        command.insert_exercises(input_data)

        mock_exercise_category_objects.assert_not_called()
        mock_remove_duplicated_exercises.assert_called_once_with([])
        mock_exercise_objects.bulk_create.assert_not_called()
        mock_stdout_write.assert_called_once_with("No new exercises to add.")
