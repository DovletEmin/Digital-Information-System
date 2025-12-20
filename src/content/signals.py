import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article, Book, Dissertation, ContentRating
from . import search_utils

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def article_saved(sender, instance, **kwargs):
    try:
        search_utils.index_object_async(instance)
    except Exception:
        logger.exception("Failed to async index Article id=%s", instance.id)


@receiver(post_delete, sender=Article)
def article_deleted(sender, instance, **kwargs):
    try:
        search_utils.delete_object_async(instance)
    except Exception:
        logger.exception("Failed to async delete Article id=%s", instance.id)


@receiver(post_save, sender=Book)
def book_saved(sender, instance, **kwargs):
    try:
        search_utils.index_object_async(instance)
    except Exception:
        logger.exception("Failed to async index Book id=%s", instance.id)


@receiver(post_delete, sender=Book)
def book_deleted(sender, instance, **kwargs):
    try:
        search_utils.delete_object_async(instance)
    except Exception:
        logger.exception("Failed to async delete Book id=%s", instance.id)


@receiver(post_save, sender=Dissertation)
def dissertation_saved(sender, instance, **kwargs):
    try:
        search_utils.index_object_async(instance)
    except Exception:
        logger.exception("Failed to async index Dissertation id=%s", instance.id)


@receiver(post_delete, sender=Dissertation)
def dissertation_deleted(sender, instance, **kwargs):
    try:
        search_utils.delete_object_async(instance)
    except Exception:
        logger.exception("Failed to async delete Dissertation id=%s", instance.id)


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
                obj = Model.objects.get(id=cid)
                search_utils.index_object_async(obj)
            except Model.DoesNotExist:
                logger.warning("Rated object not found for indexing: %s id=%s", ct, cid)
    except Exception:
        logger.exception("Failed handling ContentRating save for id=%s", getattr(instance, "id", None))
