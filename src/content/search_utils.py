import logging
import threading
from elasticsearch import Elasticsearch
from django.conf import settings

logger = logging.getLogger(__name__)


def get_es_client():
    try:
        es_url = settings.ELASTICSEARCH_DSL["default"]["hosts"]
        return Elasticsearch(es_url, timeout=30)
    except Exception as e:
        logger.exception("Failed to create ES client: %s", e)
        return None


def _build_doc(obj):
    doc = {
        "title": getattr(obj, "title", None),
        "author": getattr(obj, "author", None),
        "language": getattr(obj, "language", None),
        "average_rating": round(float(getattr(obj, "average_rating", 0) or 0), 2),
        "rating_count": getattr(obj, "rating_count", 0) or 0,
        "views": getattr(obj, "views", 0) or 0,
    }

    # Article specific
    from .models import Article, Book, Dissertation

    if isinstance(obj, Article):
        doc.update(
            {
                "content": getattr(obj, "content", None),
                "author_workplace": getattr(obj, "author_workplace", None) or None,
                "type": getattr(obj, "type", None),
                "publication_date": obj.publication_date.isoformat()
                if getattr(obj, "publication_date", None)
                else None,
                "source_name": getattr(obj, "source_name", None),
                "source_url": getattr(obj, "source_url", None),
                "newspaper_or_journal": getattr(obj, "newspaper_or_journal", None),
                "image": obj.image.url if getattr(obj, "image", None) else None,
            }
        )

    if isinstance(obj, Book):
        doc.update(
            {
                "content": getattr(obj, "content", None),
                "epub_file": obj.epub_file.url if getattr(obj, "epub_file", None) else None,
                "cover_image": obj.cover_image.url if getattr(obj, "cover_image", None) else None,
            }
        )

    if isinstance(obj, Dissertation):
        doc.update(
            {
                "content": getattr(obj, "content", None),
                "author_workplace": getattr(obj, "author_workplace", None) or None,
                "publication_date": obj.publication_date.isoformat()
                if getattr(obj, "publication_date", None)
                else None,
            }
        )

    # categories
    try:
        cats = [
            {"id": c.id, "name": c.name, "parent": getattr(c, "parent_id", None) or None}
            for c in obj.categories.all()
        ]
    except Exception:
        cats = []

    doc["categories"] = cats
    return doc


def index_object(obj):
    client = get_es_client()
    if not client:
        logger.warning("Elasticsearch client unavailable; skipping indexing")
        return False

    # Determine index name
    model_name = obj.__class__.__name__.lower()
    if model_name == "article":
        index = "articles"
    elif model_name == "book":
        index = "books"
    elif model_name == "dissertation":
        index = "dissertations"
    else:
        logger.warning("Unsupported model for indexing: %s", obj.__class__)
        return False

    try:
        doc = _build_doc(obj)
        client.index(index=index, id=obj.id, body=doc)
        client.indices.refresh(index=index)
        logger.info("Indexed %s id=%s", index, obj.id)
        return True
    except Exception:
        logger.exception("Error indexing object %s id=%s", index, getattr(obj, "id", None))
        return False


def delete_object(obj):
    client = get_es_client()
    if not client:
        logger.warning("Elasticsearch client unavailable; skipping delete")
        return False

    model_name = obj.__class__.__name__.lower()
    if model_name == "article":
        index = "articles"
    elif model_name == "book":
        index = "books"
    elif model_name == "dissertation":
        index = "dissertations"
    else:
        return False

    try:
        if client.exists(index=index, id=obj.id):
            client.delete(index=index, id=obj.id)
            logger.info("Deleted %s id=%s from index", index, obj.id)
        return True
    except Exception:
        logger.exception("Error deleting object from index %s id=%s", index, getattr(obj, "id", None))
        return False


def index_object_async(obj):
    threading.Thread(target=index_object, args=(obj,), daemon=True).start()


def delete_object_async(obj):
    threading.Thread(target=delete_object, args=(obj,), daemon=True).start()
