from __future__ import annotations
import os
from celery import Celery

# set default Django settings module for 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

celery = Celery("src")
# configure from Django settings with prefix CELERY_
celery.config_from_object("django.conf:settings", namespace="CELERY")
# autodiscover tasks in installed apps
celery.autodiscover_tasks()
