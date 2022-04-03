import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planplus.settings")
app = Celery("planplus")

app.conf.beat_schedule = {
    # Executes every 15 minutes
    'db_update': {
        'task': 'plan.tasks.update_db',
        'schedule': crontab(minute='*/5'),
    },
}

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
