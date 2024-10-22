from django.utils import timezone

import pytest


from workouts.models import ScheduledWorkoutDate


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestScheduledWorkoutDateModel:
    def test_create_scheduled_date(self, workout_created):
        date = timezone.localdate()
        time = timezone.now().time()

        date_data = {
            "date": date,
            "time": time,
            "workout": workout_created,
        }
        scheduled_date = ScheduledWorkoutDate.objects.create(**date_data)

        assert scheduled_date.id is not None
        assert all(
            getattr(scheduled_date, field) == date_data[field] for field in date_data
        )

    def test_scheduled_date_str(self, workout_created):
        date = timezone.localdate()
        time = timezone.now().time()

        date_data = {
            "date": date,
            "time": time,
            "workout": workout_created,
        }
        scheduled_date = ScheduledWorkoutDate(**date_data)

        assert (
            str(scheduled_date)
            == f"{scheduled_date.workout.name} - {scheduled_date.date} {scheduled_date.time}"
        )

    def test_scheduled_date_workout_relationship(self, workout_created):
        date = timezone.localdate()
        time = timezone.now().time()

        date_data = {
            "date": date,
            "time": time,
            "workout": workout_created,
        }
        scheduled_date = ScheduledWorkoutDate.objects.create(**date_data)

        assert workout_created.scheduled_dates.count() == 1
        assert workout_created.scheduled_dates.first() == scheduled_date

    def test_workout_cascade_delete(self, workout_created):
        date = timezone.localdate()
        time = timezone.now().time()

        date_data = {
            "date": date,
            "time": time,
            "workout": workout_created,
        }
        ScheduledWorkoutDate.objects.create(**date_data)

        assert ScheduledWorkoutDate.objects.count() == 1
        workout_created.delete()

        assert ScheduledWorkoutDate.objects.count() == 0
