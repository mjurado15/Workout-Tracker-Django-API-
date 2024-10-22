import pytest

from workouts.models import Workout


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestWorkoutModel:
    def test_create_workout(self, user_created):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
        }
        workout = Workout.objects.create(**workout_data)

        assert workout.id is not None
        assert all(
            getattr(workout, field) == workout_data[field] for field in workout_data
        )

    def test_workout_str(self, user_created):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
        }
        workout = Workout(**workout_data)

        assert str(workout) == f"{workout_data['name']} ({workout_data['user']})"

    def test_create_workout_default_values(self, user_created):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
        }
        workout = Workout.objects.create(**workout_data)

        assert workout.description == ""
        assert workout.created_at is not None
        assert workout.updated_at is not None

    def test_create_workout_with_optional_description(self, user_created):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
            "description": "This is a description",
        }
        workout = Workout.objects.create(**workout_data)

        assert workout.description == workout_data["description"]

    def test_user_workout_relationship(self, user_created):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
        }
        workout = Workout.objects.create(**workout_data)

        assert user_created.workouts.count() == 1
        assert user_created.workouts.first() == workout

    def test_user_cascade_delete(self, user_created):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
        }
        Workout.objects.create(**workout_data)

        assert Workout.objects.count() == 1
        user_created.delete()

        assert Workout.objects.count() == 0
