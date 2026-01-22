"""
API v1 views with improved patterns and error handling.
"""

from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Prefetch, F
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta

from content.models import (
    Article,
    Book,
    Dissertation,
    ArticleCategory,
    BookCategory,
    DissertationCategory,
    ContentRating,
    PendingView,
    ViewRecord,
    Profile,
)
from content.serializers import (
    ArticleSerializer,
    BookSerializer,
    DissertationSerializer,
    ArticleCategorySerializer,
    BookCategorySerializer,
    DissertationCategorySerializer,
    ArticleListSerializer,
    BookListSerializer,
    DissertationListSerializer,
    UserSerializer,
)
from content.utils.mixins import (
    BookmarkAnnotateMixin,
    CachedRetrieveMixin,
    ContentListOptimizationMixin,
)
from content.utils.throttles import SearchRateThrottle, AuthRateThrottle


# Optimized category querysets
article_cat_qs = ArticleCategory.objects.all()
book_cat_qs = BookCategory.objects.select_related("parent").prefetch_related(
    "subcategories"
)
dissertation_cat_qs = DissertationCategory.objects.select_related(
    "parent"
).prefetch_related("subcategories")


@method_decorator(cache_page(60 * 10), name="list")
class ArticleViewSet(
    BookmarkAnnotateMixin,
    CachedRetrieveMixin,
    ContentListOptimizationMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """
    ViewSet for Article model.
    Implements bookmarking, caching, and list optimization.
    """

    queryset = (
        Article.objects.all()
        .order_by("-id")
        .prefetch_related(Prefetch("categories", queryset=article_cat_qs))
    )
    serializer_class = ArticleSerializer
    list_serializer_class = ArticleListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "type": ["exact"],
        "categories": ["exact"],
        "publication_date": ["gte", "lte", "exact"],
    }

    bookmark_field_name = "bookmarked_articles"
    list_only_fields = [
        "id",
        "title",
        "author",
        "average_rating",
        "rating_count",
        "views",
        "language",
        "image",
    ]
    cache_timeout = 60


@method_decorator(cache_page(60 * 10), name="list")
class BookViewSet(
    BookmarkAnnotateMixin,
    CachedRetrieveMixin,
    ContentListOptimizationMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """ViewSet for Book model with optimization mixins"""

    queryset = (
        Book.objects.all()
        .order_by("-id")
        .prefetch_related(Prefetch("categories", queryset=book_cat_qs))
    )
    serializer_class = BookSerializer
    list_serializer_class = BookListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "categories": ["exact"],
    }

    bookmark_field_name = "bookmarked_books"
    list_only_fields = [
        "id",
        "title",
        "author",
        "average_rating",
        "rating_count",
        "views",
        "language",
        "cover_image",
    ]
    cache_timeout = 60


@method_decorator(cache_page(60 * 10), name="list")
class DissertationViewSet(
    BookmarkAnnotateMixin,
    CachedRetrieveMixin,
    ContentListOptimizationMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """ViewSet for Dissertation model with optimization mixins"""

    queryset = (
        Dissertation.objects.all()
        .order_by("-id")
        .prefetch_related(Prefetch("categories", queryset=dissertation_cat_qs))
    )
    serializer_class = DissertationSerializer
    list_serializer_class = DissertationListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "categories": ["exact"],
        "publication_date": ["gte", "lte", "exact"],
    }

    bookmark_field_name = "bookmarked_dissertations"
    list_only_fields = [
        "id",
        "title",
        "author",
        "average_rating",
        "rating_count",
        "views",
        "language",
        "publication_date",
    ]
    cache_timeout = 60


@method_decorator(cache_page(60 * 60), name="list")
class ArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Article categories"""

    queryset = ArticleCategory.objects.all().order_by("name")
    serializer_class = ArticleCategorySerializer
    pagination_class = None


@method_decorator(cache_page(60 * 60), name="list")
class BookCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Book categories with hierarchy support"""

    queryset = book_cat_qs.order_by("name")
    serializer_class = BookCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"parent": ["exact", "isnull"]}
    pagination_class = None


@method_decorator(cache_page(60 * 60), name="list")
class DissertationCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Dissertation categories with hierarchy support"""

    queryset = dissertation_cat_qs.order_by("name")
    serializer_class = DissertationCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"parent": ["exact", "isnull"]}
    pagination_class = None


class RegisterView(generics.CreateAPIView):
    """User registration endpoint with throttling"""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    throttle_classes = [AuthRateThrottle]


class ToggleBookmarkView(APIView):
    """Toggle bookmark for any content type"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add or remove bookmark for content",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["type"],
            properties={
                "type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["article", "book", "dissertation"],
                ),
            },
        ),
    )
    def post(self, request, pk):
        content_type = (request.data.get("type") or "").strip().lower()

        mapping = {
            "article": (Article, "bookmarked_articles"),
            "book": (Book, "bookmarked_books"),
            "dissertation": (Dissertation, "bookmarked_dissertations"),
        }

        if content_type not in mapping:
            return Response(
                {"error": "Invalid type. Must be: article, book, or dissertation"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model, field_name = mapping[content_type]
        try:
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return Response(
                {"error": "Content not found"}, status=status.HTTP_404_NOT_FOUND
            )

        profile = request.user.profile
        user_field = getattr(profile, field_name)

        if user_field.filter(pk=pk).exists():
            user_field.remove(obj)
            added = False
        else:
            user_field.add(obj)
            added = True

        return Response({"added": added, "is_bookmarked": added})


class UserBookmarksView(APIView):
    """Get all user bookmarks"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.core.cache import cache

        cache_key = f"user_bookmarks:{request.user.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        profile = request.user.profile

        articles_qs = (
            profile.bookmarked_articles.all()
            .prefetch_related(Prefetch("categories", queryset=article_cat_qs))
            .only(
                "id",
                "title",
                "author",
                "average_rating",
                "rating_count",
                "views",
                "language",
            )
        )
        books_qs = (
            profile.bookmarked_books.all()
            .prefetch_related(Prefetch("categories", queryset=book_cat_qs))
            .only(
                "id",
                "title",
                "author",
                "average_rating",
                "rating_count",
                "views",
                "language",
            )
        )
        dissertations_qs = (
            profile.bookmarked_dissertations.all()
            .prefetch_related(Prefetch("categories", queryset=dissertation_cat_qs))
            .only(
                "id",
                "title",
                "author",
                "average_rating",
                "rating_count",
                "views",
                "language",
            )
        )

        data = {
            "articles": ArticleListSerializer(articles_qs, many=True).data,
            "books": BookListSerializer(books_qs, many=True).data,
            "dissertations": DissertationListSerializer(
                dissertations_qs, many=True
            ).data,
        }

        try:
            cache.set(cache_key, data, 30)
        except Exception:
            pass

        return Response(data)


class RegisterViewHit(APIView):
    """Register a view hit for content with deduplication"""

    def post(self, request, content_type, pk):
        content_type = (content_type or "").strip().lower()
        if content_type not in ("article", "book", "dissertation"):
            return Response(
                {"error": "Invalid content type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        ttl_hours = 24
        cutoff = now - timedelta(hours=ttl_hours)

        try:
            if request.user.is_authenticated:
                seen = ViewRecord.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    content_id=pk,
                    last_seen__gte=cutoff,
                ).exists()

                if seen:
                    return Response(
                        {"accepted": False, "reason": "Already counted"},
                        status=status.HTTP_200_OK,
                    )

                ViewRecord.objects.update_or_create(
                    user=request.user,
                    content_type=content_type,
                    content_id=pk,
                    defaults={"last_seen": now},
                )
            else:
                if not request.session.session_key:
                    request.session.save()
                sk = request.session.session_key

                seen = ViewRecord.objects.filter(
                    session_key=sk,
                    content_type=content_type,
                    content_id=pk,
                    last_seen__gte=cutoff,
                ).exists()

                if seen:
                    return Response(
                        {"accepted": False, "reason": "Already counted"},
                        status=status.HTTP_200_OK,
                    )

                ViewRecord.objects.update_or_create(
                    session_key=sk,
                    content_type=content_type,
                    content_id=pk,
                    defaults={"last_seen": now},
                )

            # Increment pending view count
            pv, created = PendingView.objects.get_or_create(
                content_type=content_type, content_id=pk, defaults={"count": 1}
            )
            if not created:
                PendingView.objects.filter(pk=pv.pk).update(count=F("count") + 1)

        except Exception as e:
            return Response(
                {"error": "Database error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"accepted": True})


class RateContentView(APIView):
    """Rate content (1-5 stars)"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Rate content with 1-5 stars",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["content_type", "content_id", "rating"],
            properties={
                "content_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["article", "book", "dissertation"],
                ),
                "content_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "rating": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    enum=[1, 2, 3, 4, 5],
                ),
            },
        ),
        security=[{"Bearer": []}],
    )
    def post(self, request):
        content_type = request.data.get("content_type", "").strip().lower()
        content_id = request.data.get("content_id")
        rating_value = request.data.get("rating")

        # Validation
        if not all([content_type, content_id, rating_value]):
            return Response(
                {"error": "content_type, content_id, and rating are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if content_type not in ["article", "book", "dissertation"]:
            return Response(
                {"error": "Invalid content_type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            content_id = int(content_id)
            rating_value = int(rating_value)
        except (ValueError, TypeError):
            return Response(
                {"error": "content_id and rating must be integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not 1 <= rating_value <= 5:
            return Response(
                {"error": "Rating must be between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create or update rating
        obj, created = ContentRating.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            content_id=content_id,
            defaults={"rating": rating_value},
        )

        return Response(
            {
                "success": True,
                "message": "Rating updated" if not created else "Rating created",
                "rating": rating_value,
            },
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
        )
