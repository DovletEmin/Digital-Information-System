from __future__ import annotations
from celery import shared_task
from django.core.management import call_command
from celery.utils.log import get_task_logger
from typing import Optional

logger = get_task_logger(__name__)


@shared_task(bind=True)
def flush_views_task(self):
    """Run the `flush_views` management command from Celery.

    This lets django-celery-beat schedule `flush_views` by enqueuing this task.
    """
    call_command("flush_views")


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def index_object_task(
    self, app_label: str, model_name: str, obj_id: int
) -> Optional[bool]:
    """Index a single model instance.

    This task lets Celery handle retries when Elasticsearch is temporarily
    unavailable. It looks up the model dynamically and calls
    `search_utils.index_object`.
    """
    try:
        from django.apps import apps
        from content import search_utils

        model = apps.get_model(app_label, model_name)
        if model is None:
            logger.error("Model not found: %s.%s", app_label, model_name)
            return False

        try:
            obj = model.objects.get(id=obj_id)
        except model.DoesNotExist:
            logger.warning(
                "Object not found for indexing: %s.%s id=%s",
                app_label,
                model_name,
                obj_id,
            )
            return False

        ok = search_utils.index_object(obj)
        if not ok:
            # Let Celery retry the task for transient ES failures
            raise Exception("Indexing failed; will retry")

        return True
    except Exception as exc:
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.exception(
                "Max retries exceeded for indexing %s.%s id=%s",
                app_label,
                model_name,
                obj_id,
            )
            return False


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def delete_object_task(
    self, app_label: str, model_name: str, obj_id: int
) -> Optional[bool]:
    """Delete an object from Elasticsearch index with retries.

    Looks up the model instance (if present) and calls `search_utils.delete_object`.
    If the model instance isn't present on the DB, attempts best-effort delete by id.
    """
    try:
        from django.apps import apps
        from content import search_utils

        model = apps.get_model(app_label, model_name)
        # try to call delete_object with a live instance if available
        if model is not None:
            try:
                obj = model.objects.get(id=obj_id)
                ok = search_utils.delete_object(obj)
            except model.DoesNotExist:
                # create a lightweight placeholder object with id attribute
                class _Placeholder:
                    def __init__(self, id):
                        self.id = id

                placeholder = _Placeholder(obj_id)
                ok = search_utils.delete_object(placeholder)
        else:
            # No model, perform best-effort delete
            class _Placeholder:
                def __init__(self, id):
                    self.id = id

            ok = search_utils.delete_object(_Placeholder(obj_id))

        if not ok:
            raise Exception("Delete failed; will retry")

        return True
    except Exception as exc:
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.exception(
                "Max retries exceeded for delete %s.%s id=%s",
                app_label,
                model_name,
                obj_id,
            )
            return False
