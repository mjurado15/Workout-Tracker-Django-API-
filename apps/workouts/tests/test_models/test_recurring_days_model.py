from django.utils import timezone

import pytest


from workouts.models import RecurringWorkoutDays


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestRecurringWorkoutDaysModel:
    def test_create_recurring_days(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        days_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        recurring_days = RecurringWorkoutDays.objects.create(**days_data)

        assert recurring_days.id is not None
        assert all(
            getattr(recurring_days, field) == days_data[field] for field in days_data
        )

    def test_recurring_days_str(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        days_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        recurring_days = RecurringWorkoutDays(**days_data)

        assert (
            str(recurring_days)
            == f"{recurring_days.workout.name} - {recurring_days.get_week_days_display()} {recurring_days.time}"
        )

    def test_default_values(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        days_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        recurring_days = RecurringWorkoutDays.objects.create(**days_data)

        assert not recurring_days.activated

    def test_recurring_days_workout_relationship(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        days_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        recurring_days = RecurringWorkoutDays.objects.create(**days_data)

        assert workout_created.recurring_days.count() == 1
        assert workout_created.recurring_days.first() == recurring_days

    def test_workout_cascade_delete(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        days_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        RecurringWorkoutDays.objects.create(**days_data)

        assert RecurringWorkoutDays.objects.count() == 1
        workout_created.delete()

        assert RecurringWorkoutDays.objects.count() == 0

    def test_get_days_display_method(self):
        days_data = {
            "week_days": [0, 1, 2, 6],
        }
        recurring_days = RecurringWorkoutDays(**days_data)

        assert (
            recurring_days.get_week_days_display()
            == "Monday, Tuesday, Wednesday, Sunday"
        )

    def test_get_days_display_method__no_week_days(self):
        days_data = {"week_days": []}
        recurring_days = RecurringWorkoutDays(**days_data)

        assert recurring_days.get_week_days_display() == "No set days"

    def test_activate_method(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        days_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        recurring_days = RecurringWorkoutDays.objects.create(**days_data)

        assert not recurring_days.activated
        recurring_days.activate()

        assert recurring_days.activated
