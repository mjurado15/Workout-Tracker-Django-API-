import pytest
from django.utils import timezone

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
        assert workout.type == ""
        assert workout.created_at is not None
        assert workout.updated_at is not None

    @pytest.mark.parametrize(
        "optional_field, value",
        [
            ("description", "This is a description"),
            ("type", "S"),
        ],
    )
    def test_create_workout_with_optional_description(
        self, user_created, optional_field, value
    ):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
            optional_field: value,
        }
        workout = Workout.objects.create(**workout_data)

        assert getattr(workout, optional_field) == workout_data[optional_field]

    def test_workout_user_relationship(self, user_created):
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

    def test_is_recurrent_method(self, user_created):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
            "type": Workout.RECURRENT,
        }
        workout = Workout.objects.create(**workout_data)

        assert workout.is_recurrent()

    def test_is_scheduled_method(self, user_created):
        workout_data = {
            "name": "Test Workout",
            "user": user_created,
            "type": Workout.SCHEDULED,
        }
        workout = Workout.objects.create(**workout_data)

        assert workout.is_scheduled()

    def test_switch_to_recurrent_method(self, user_created):
        workout_data = {
            "name": "Scheduled Workout",
            "user": user_created,
            "type": Workout.SCHEDULED,
        }
        workout = Workout.objects.create(**workout_data)
        workout.scheduled_dates.create(
            workout=workout, date=timezone.localdate(), time=timezone.now().time()
        )

        assert not workout.is_recurrent()
        assert workout.scheduled_dates.count() == 1
        workout.switch_to_recurrent()

        assert workout.is_recurrent()
        assert workout.scheduled_dates.count() == 0

    def test_switch_to_scheduled_method(self, user_created):
        workout_data = {
            "name": "Recurring Workout",
            "user": user_created,
            "type": Workout.RECURRENT,
        }
        workout = Workout.objects.create(**workout_data)
        workout.recurring_days.create(workout=workout, time=timezone.now().time())

        assert not workout.is_scheduled()
        assert workout.recurring_days.count() == 1
        workout.switch_to_scheduled()

        assert workout.is_scheduled()
        assert workout.recurring_days.count() == 0
