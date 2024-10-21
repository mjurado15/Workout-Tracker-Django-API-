import os
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from workouts.models import ExerciseCategory, Exercise


def remove_duplicate_items_by_name(data):
    seen = set()
    unique_data = []

    for item in data:
        name = item.get("name")
        if not name:
            continue

        if name not in seen:
            seen.add(name)
            unique_data.append(item)

    return unique_data


def remove_duplicate_exercises_by_name_and_category(exercises_list):
    seen = []
    unique_data = []

    for exercise in exercises_list:
        name = exercise.name
        category = exercise.category
        if not (name and category):
            continue

        essential_data = {"name": name, "category": category}
        if essential_data not in seen:
            seen.append(essential_data)
            unique_data.append(exercise)

    return unique_data


class Command(BaseCommand):
    def insert_exercise_categories(self, categories):
        # remove duplicate categories
        categories = remove_duplicate_items_by_name(categories)

        existing = ExerciseCategory.objects.filter(
            name__in=[category["name"] for category in categories]
        )
        existing_names = set(existing.values_list("name", flat=True))

        new_categories = [
            ExerciseCategory(name=item["name"])
            for item in categories
            if item["name"] not in existing_names
        ]
        if new_categories:
            ExerciseCategory.objects.bulk_create(new_categories)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully added {len(new_categories)} new exercise categories."
                )
            )
        else:
            self.stdout.write(self.style.WARNING("No new exercise categories to add."))

    def insert_exercises(self, exercise_categories):
        exercises_to_add = []
        for exercise_category in exercise_categories:
            try:
                category_db = ExerciseCategory.objects.get(
                    name=exercise_category["name"]
                )
            except ExerciseCategory.DoesNotExist:
                continue

            exercises = exercise_category["exercises"]

            existing_exercises = Exercise.objects.filter(
                name__in=[item["name"] for item in exercises], category=category_db
            )
            existing_names = set(existing_exercises.values_list("name", flat=True))

            exercises_to_add += [
                Exercise(**item, category=category_db)
                for item in exercises
                if item["name"] not in existing_names
            ]

        # remove duplicate exercises
        exercises_to_add = remove_duplicate_exercises_by_name_and_category(
            exercises_to_add
        )

        if exercises_to_add:
            Exercise.objects.bulk_create(exercises_to_add)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully added {len(exercises_to_add)} new exercises."
                )
            )
        else:
            self.stdout.write(self.style.WARNING("No new exercises to add."))

    def handle(self, *args, **options):
        seed_file_path = os.path.join(
            settings.BASE_DIR, "apps", "workouts", "data", "seed_data.json"
        )
        with open(seed_file_path, "r") as f:
            seed_data = json.load(f)
            exercise_categories = seed_data["exercise_categories"]

            self.insert_exercise_categories(
                [{"name": item["name"]} for item in exercise_categories]
            )

            self.insert_exercises(exercise_categories)

        self.stdout.write(self.style.SUCCESS("Exercises added successfully!"))
