import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_slack.settings')

app = Celery('ai_slack')
app.config_from_object("django.conf:settings",namespace='CELERY')
app.autodiscover_tasks()