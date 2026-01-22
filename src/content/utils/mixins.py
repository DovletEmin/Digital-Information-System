"""
Mixins for content viewsets.
Implements reusable patterns using Mixin design pattern.
"""

from django.core.cache import cache
from django.db.models import Exists, OuterRef, Value, BooleanField
from rest_framework.response import Response


class BookmarkAnnotateMixin:
    """
    Mixin to annotate queryset with user's bookmark status.

    Pattern: Mixin pattern for reusable functionality
    Usage: Add bookmark_field_name attribute to your ViewSet
    """

    bookmark_field_name = None

    def annotate_bookmarks(self, queryset):
        """
        Annotate queryset with is_bookmarked field for authenticated users.

        Args:
            queryset: Django queryset to annotate

        Returns:
            Annotated queryset with is_bookmarked boolean field
        """
        if not self.bookmark_field_name:
            return queryset.annotate(
                is_bookmarked=Value(False, output_field=BooleanField())
            )

        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            subquery = getattr(user.profile, self.bookmark_field_name).filter(
                pk=OuterRef("pk")
            )
            return queryset.annotate(is_bookmarked=Exists(subquery))

        return queryset.annotate(
            is_bookmarked=Value(False, output_field=BooleanField())
        )


class CachedRetrieveMixin:
    """
    Mixin to add caching to retrieve actions.

    Pattern: Decorator/Wrapper pattern for caching
    Usage: Implement get_cache_key() and cache_timeout in your ViewSet
    """

    cache_timeout = 60  # Default cache timeout in seconds

    def get_cache_key(self, pk):
        """
        Generate cache key for an object.
        Override this method to customize cache key generation.

        Args:
            pk: Primary key of the object

        Returns:
            str: Cache key
        """
        model_name = self.queryset.model.__name__.lower()
        user_id = (
            self.request.user.id
            if getattr(self.request, "user", None)
            and self.request.user.is_authenticated
            else "anon"
        )
        version = self._get_cache_version()
        return f"{model_name}:detail:v{version}:{pk}:user:{user_id}"

    def _get_cache_version(self):
        """Get global cache version for invalidation"""
        try:
            v = cache.get("content_cache_version")
            return int(v or 0)
        except Exception:
            return 0

    def retrieve(self, request, *args, **kwargs):
        """
        Cached retrieve method.
        Checks cache first, then falls back to database.
        """
        pk = kwargs.get("pk")
        cache_key = self.get_cache_key(pk)

        # Try to get from cache
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        # Not in cache, get from DB
        response = super().retrieve(request, *args, **kwargs)

        # Store in cache
        try:
            cache.set(cache_key, response.data, self.cache_timeout)
        except Exception:
            pass  # Cache failure shouldn't break the request

        return response


class ContentListOptimizationMixin:
    """
    Mixin to optimize list queries for content models.

    Pattern: Template Method pattern
    Usage: Define list_only_fields in your ViewSet
    """

    list_only_fields = None
    list_serializer_class = None

    def get_queryset(self):
        """Optimize queryset for list action"""
        queryset = super().get_queryset()

        # For list action, only fetch necessary fields
        if getattr(self, "action", None) == "list" and self.list_only_fields:
            queryset = queryset.only(*self.list_only_fields)

        # Annotate bookmarks only for detail view (not list for caching)
        if getattr(self, "action", None) != "list" and hasattr(
            self, "annotate_bookmarks"
        ):
            queryset = self.annotate_bookmarks(queryset)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer for list/detail actions"""
        if getattr(self, "action", None) == "list" and self.list_serializer_class:
            return self.list_serializer_class
        return super().get_serializer_class()
