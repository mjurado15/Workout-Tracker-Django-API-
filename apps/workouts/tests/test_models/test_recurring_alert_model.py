from datetime import timedelta

import pytest
from django.utils import timezone

from workouts.models import RecurringWorkoutAlert


pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestRecurringWorkoutAlertModel:
    def test_create_recurring_alert(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        alert_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        recurring_alert = RecurringWorkoutAlert.objects.create(**alert_data)

        assert recurring_alert.id is not None
        assert all(
            getattr(recurring_alert, field) == alert_data[field] for field in alert_data
        )

    def test_recurring_alert_str(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        alert_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        recurring_alert = RecurringWorkoutAlert(**alert_data)

        assert (
            str(recurring_alert)
            == f"{recurring_alert.workout.name} - {recurring_alert.get_week_days_display()} {recurring_alert.time}"
        )

    def test_recurring_alert_workout_relationship(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        alert_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        recurring_alert = RecurringWorkoutAlert.objects.create(**alert_data)

        assert workout_created.recurring_alerts.count() == 1
        assert workout_created.recurring_alerts.first() == recurring_alert

    def test_workout_cascade_delete(self, workout_created):
        week_days = [0, 1, 4]
        time = timezone.now().time()

        alert_data = {
            "time": time,
            "week_days": week_days,
            "workout": workout_created,
        }
        RecurringWorkoutAlert.objects.create(**alert_data)

        assert RecurringWorkoutAlert.objects.count() == 1
        workout_created.delete()

        assert RecurringWorkoutAlert.objects.count() == 0

    def test_get_days_display_method(self):
        alert_data = {
            "week_days": [0, 1, 2, 6],
        }
        recurring_alert = RecurringWorkoutAlert(**alert_data)

        assert (
            recurring_alert.get_week_days_display()
            == "Monday, Tuesday, Wednesday, Sunday"
        )

    def test_get_days_display_method__no_week_days(self):
        alert_data = {"week_days": []}
        recurring_alert = RecurringWorkoutAlert(**alert_data)

        assert recurring_alert.get_week_days_display() == "No set days"
