"""
Helper utilities for content app.
"""

from django.db.models import Count
from django.core.cache import cache
from datetime import timedelta
from django.db.models.functions import TruncDate


def aggregate_language_counts(models, languages=("tm", "ru", "en")):
    """
    Aggregate content counts by language across multiple models.

    Args:
        models: List of Django models to aggregate
        languages: Tuple of language codes to count

    Returns:
        dict: Language code -> count mapping
    """
    totals = {lang: 0 for lang in languages}
    for model in models:
        qs = model.objects.values("language").annotate(c=Count("id"))
        for r in qs:
            lang = r.get("language")
            if lang in totals:
                totals[lang] += r.get("c", 0)
    return totals


def merge_top_items(
    models_with_labels, per_model=7, total_limit=8, fields=("id", "title", "views")
):
    """
    Merge top items from multiple models into a single sorted list.

    Args:
        models_with_labels: List of (model, label) tuples
        per_model: Number of items to fetch per model
        total_limit: Maximum items in final list
        fields: Fields to fetch

    Returns:
        list: Merged and sorted items
    """
    items = []
    for model, label in models_with_labels:
        qs = model.objects.order_by("-views").only(*fields)[:per_model]
        for obj in qs:
            items.append(
                {
                    "id": getattr(obj, "id", None),
                    "title": getattr(obj, "title", None),
                    "views": getattr(obj, "views", 0),
                    "type": label,
                }
            )
    return sorted(items, key=lambda x: x["views"], reverse=True)[:total_limit]


def publication_counts_map(models, date_field, since_date):
    """
    Build a date -> count map for publications.

    Args:
        models: List of models to query
        date_field: Name of the date field
        since_date: Start date

    Returns:
        dict: Date -> count mapping
    """
    counts_map = {}
    for model in models:
        qs = (
            model.objects.filter(**{f"{date_field}__gte": since_date})
            .annotate(d=TruncDate(date_field))
            .values("d")
            .annotate(c=Count("id"))
        )
        for r in qs:
            counts_map[r["d"]] = counts_map.get(r["d"], 0) + r["c"]
    return counts_map


def daily_counts_list_from_map(counts_map, since_date, days=30, date_fmt="%Y-%m-%d"):
    """
    Convert counts map to lists of dates and counts.

    Args:
        counts_map: Date -> count mapping
        since_date: Start date
        days: Number of days to include
        date_fmt: Date format string

    Returns:
        tuple: (dates list, counts list)
    """
    dates = []
    counts = []
    for i in range(days):
        d = since_date + timedelta(days=i)
        dates.append(d.strftime(date_fmt))
        counts.append(counts_map.get(d, 0))
    return dates, counts


def increment_cache_version(key="content_cache_version"):
    """
    Increment global cache version for invalidation.

    Args:
        key: Cache key name
    """
    try:
        v = cache.get(key) or 0
        cache.set(key, int(v) + 1)
    except Exception:
        pass
