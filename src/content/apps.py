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
