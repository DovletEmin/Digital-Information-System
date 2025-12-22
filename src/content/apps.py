from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "content"

    def ready(self):
        # import signals to connect handlers
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
        # Ensure the scheduled `flush_views` PeriodicTask exists (idempotent)
        try:
            from django.conf import settings
            from django_celery_beat.models import CrontabSchedule, PeriodicTask

            tz = getattr(settings, "TIME_ZONE", "UTC")
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute="*/5",
                hour="*",
                day_of_week="*",
                day_of_month="*",
                month_of_year="*",
                timezone=tz,
            )

            PeriodicTask.objects.update_or_create(
                name="flush_views_every_5_minutes",
                defaults={
                    "crontab": schedule,
                    "task": "content.tasks.flush_views_task",
                    "enabled": True,
                },
            )
        except Exception:
            # Avoid breaking app startup if DB/migrations not ready
            pass
