from django.utils import timezone

import pytest


from workouts.models import ScheduledWorkoutDate


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestScheduledWorkoutDateModel:
    def test_create_scheduled_date(self, workout_created):
        date_data = {
            "datetime": timezone.now(),
            "workout": workout_created,
        }
        scheduled_date = ScheduledWorkoutDate.objects.create(**date_data)

        assert scheduled_date.id is not None
        assert all(
            getattr(scheduled_date, field) == date_data[field] for field in date_data
        )

    def test_scheduled_date_str(self, workout_created):
        date_data = {
            "datetime": timezone.now(),
            "workout": workout_created,
        }
        scheduled_date = ScheduledWorkoutDate(**date_data)

        assert (
            str(scheduled_date)
            == f"{scheduled_date.workout.name} - {scheduled_date.datetime}"
        )

    def test_create_scheduled_default_values(self, workout_created):
        date_data = {
            "datetime": timezone.now(),
            "workout": workout_created,
        }
        scheduled_date = ScheduledWorkoutDate.objects.create(**date_data)

        assert scheduled_date.id is not None
        assert not scheduled_date.activated

    def test_scheduled_date_workout_relationship(self, workout_created):
        date_data = {
            "datetime": timezone.now(),
            "workout": workout_created,
        }
        scheduled_date = ScheduledWorkoutDate.objects.create(**date_data)

        assert workout_created.scheduled_dates.count() == 1
        assert workout_created.scheduled_dates.first() == scheduled_date

    def test_workout_cascade_delete(self, workout_created):
        data = {
            "datetime": timezone.now(),
            "workout": workout_created,
        }
        ScheduledWorkoutDate.objects.create(**data)

        assert ScheduledWorkoutDate.objects.count() == 1
        workout_created.delete()

        assert ScheduledWorkoutDate.objects.count() == 0

    def test_activate_method(self, workout_created):
        data = {
            "datetime": timezone.now(),
            "workout": workout_created,
        }
        scheduled_date = ScheduledWorkoutDate.objects.create(**data)

        assert not scheduled_date.activated
        scheduled_date.activate()

        assert scheduled_date.activated

    def test_deactivate_deactivate_when_datetime_is_updated(self, workout_created):
        data = {
            "datetime": timezone.now(),
            "workout": workout_created,
            "activated": True,
        }
        scheduled_date = ScheduledWorkoutDate.objects.create(**data)
        assert scheduled_date.activated

        # datetime is not updated
        scheduled_date.save()
        assert scheduled_date.activated

        # datetime is updated
        scheduled_date.datetime = timezone.now()
        scheduled_date.save()
        assert not scheduled_date.activated
