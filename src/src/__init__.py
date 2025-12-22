from .celery import celery as celery_app  # expose as `celery_app`

# provide both `celery` and `celery_app` names for compatibility with different CLIs
celery = celery_app

__all__ = ["celery", "celery_app"]
