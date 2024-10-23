from unittest.mock import call
from datetime import timedelta, datetime
from django.utils import timezone

import pytest

from workouts.tasks import (
    notify_scheduled_dates_at_the_current_minute,
    notify_recurring_alerts_at_the_current_minute,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_notify_scheduled_dates_at_the_current_minute(
    mocker, create_scheduled_date_with
):
    current_datetime = timezone.now().replace(second=0, microsecond=0)

    mocker.patch("workouts.tasks.timezone.now", return_value=current_datetime)
    mock_send_notification = mocker.patch("workouts.tasks.send_notification")

    scheduled1 = create_scheduled_date_with(datetime=current_datetime)
    create_scheduled_date_with(datetime=current_datetime - timedelta(seconds=30))
    create_scheduled_date_with(datetime=current_datetime + timedelta(minutes=1))
    scheduled4 = create_scheduled_date_with(
        datetime=current_datetime + timedelta(seconds=30)
    )

    notify_scheduled_dates_at_the_current_minute()

    assert mock_send_notification.call_count == 2
    mock_send_notification.assert_has_calls(
        [call(scheduled1), call(scheduled4)], any_order=True
    )


def test_notify_recurring_alerts_at_the_current_minute(
    mocker, create_recurring_alert_with
):
    current_datetime = timezone.now().replace(second=0, microsecond=0)
    current_weekday = current_datetime.weekday()

    mocker.patch("workouts.tasks.timezone.now", return_value=current_datetime)
    mock_send_notification = mocker.patch("workouts.tasks.send_notification")

    alert1 = create_recurring_alert_with(
        time=current_datetime.time(), week_days=[current_weekday]
    )
    alert2 = create_recurring_alert_with(
        time=(current_datetime + timedelta(seconds=30)).time(),
        week_days=[current_weekday],
    )
    create_recurring_alert_with(
        time=(current_datetime - timedelta(seconds=30)).time(),
        week_days=[current_weekday],
    )
    create_recurring_alert_with(
        time=(current_datetime + timedelta(minutes=3)).time(),
        week_days=[current_weekday],
    )
    create_recurring_alert_with(
        time=current_datetime.time(),
        week_days=[],
    )

    notify_recurring_alerts_at_the_current_minute()

    assert mock_send_notification.call_count == 2
    mock_send_notification.assert_has_calls(
        [call(alert1), call(alert2)], any_order=True
    )
