import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article, Book, Dissertation, ContentRating
from .tasks import index_object_task, delete_object_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def article_saved(sender, instance, **kwargs):
    try:
        index_object_task.delay(
            instance._meta.app_label, instance.__class__.__name__, instance.id
        )
    except Exception:
        logger.exception("Failed to enqueue index task for Article id=%s", instance.id)


@receiver(post_delete, sender=Article)
def article_deleted(sender, instance, **kwargs):
    try:
        delete_object_task.delay(
            instance._meta.app_label, instance.__class__.__name__, instance.id
        )
    except Exception:
        logger.exception("Failed to enqueue delete task for Article id=%s", instance.id)


@receiver(post_save, sender=Book)
def book_saved(sender, instance, **kwargs):
    try:
        index_object_task.delay(
            instance._meta.app_label, instance.__class__.__name__, instance.id
        )
    except Exception:
        logger.exception("Failed to enqueue index task for Book id=%s", instance.id)


@receiver(post_delete, sender=Book)
def book_deleted(sender, instance, **kwargs):
    try:
        delete_object_task.delay(
            instance._meta.app_label, instance.__class__.__name__, instance.id
        )
    except Exception:
        logger.exception("Failed to enqueue delete task for Book id=%s", instance.id)


@receiver(post_save, sender=Dissertation)
def dissertation_saved(sender, instance, **kwargs):
    try:
        index_object_task.delay(
            instance._meta.app_label, instance.__class__.__name__, instance.id
        )
    except Exception:
        logger.exception(
            "Failed to enqueue index task for Dissertation id=%s", instance.id
        )


@receiver(post_delete, sender=Dissertation)
def dissertation_deleted(sender, instance, **kwargs):
    try:
        delete_object_task.delay(
            instance._meta.app_label, instance.__class__.__name__, instance.id
        )
    except Exception:
        logger.exception(
            "Failed to enqueue delete task for Dissertation id=%s", instance.id
        )


# When a rating is added/updated, reindex the corresponding content
@receiver(post_save, sender=ContentRating)
def content_rating_saved(sender, instance, **kwargs):
    try:
        ct = instance.content_type
        cid = instance.content_id
        model_map = {"article": Article, "book": Book, "dissertation": Dissertation}
        Model = model_map.get(ct)
        if Model:
            try:
                # enqueue reindex for the rated object
                index_object_task.delay(Model._meta.app_label, Model.__name__, cid)
            except Model.DoesNotExist:
                logger.warning("Rated object not found for indexing: %s id=%s", ct, cid)
    except Exception:
        logger.exception(
            "Failed handling ContentRating save for id=%s",
            getattr(instance, "id", None),
        )
