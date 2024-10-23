import os
import sys
from pathlib import Path

from celery import Celery

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "apps"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workout_tracker.settings.develop")

app = Celery("workout_tracker")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
