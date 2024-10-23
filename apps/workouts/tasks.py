from django.utils import timezone
from celery import shared_task

from workouts.models import ScheduledWorkoutDate, RecurringWorkoutAlert


def send_notification(**kwargs):
    print("Notified!")


@shared_task
def notify_scheduled_dates_at_the_current_minute():
    current_datetime = timezone.now()
    scheduled_dates = ScheduledWorkoutDate.objects.filter(
        datetime__date=current_datetime.date(),
        datetime__hour=current_datetime.hour,
        datetime__minute=current_datetime.minute,
    )

    for scheduled_date in scheduled_dates:
        send_notification(scheduled_date)


@shared_task
def notify_recurring_alerts_at_the_current_minute():
    current_datetime = timezone.now()
    current_time = current_datetime.time()
    current_week_day = current_datetime.weekday()

    alerts = RecurringWorkoutAlert.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute,
        week_days__contains=current_week_day,
    )

    for alert in alerts:
        send_notification(alert)
