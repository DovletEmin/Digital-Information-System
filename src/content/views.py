from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from elasticsearch import Elasticsearch
from django.db.models import (
    Case,
    When,
    Value,
    IntegerField,
    Exists,
    OuterRef,
    BooleanField,
    Count,
    Avg,
    Sum,
    F,
    Prefetch,
)
from django.db.models.functions import TruncDate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render
import logging
from django.http import JsonResponse, HttpResponse
from io import BytesIO
from django.core.cache import cache
from .models import (
    Article,
    Book,
    Dissertation,
    ArticleCategory,
    BookCategory,
    DissertationCategory,
    ContentRating,
    Profile,
)
from .models import PendingView, ViewRecord
from .serializers import (
    ArticleSerializer,
    BookSerializer,
    DissertationSerializer,
    ArticleCategorySerializer,
    BookCategorySerializer,
    DissertationCategorySerializer,
    UserSerializer,
)

from .serializers import (
    ArticleListSerializer,
    BookListSerializer,
    DissertationListSerializer,
)

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


# Prepare optimized category querysets to avoid N+1 when serializing related categories
# ArticleCategory has no `parent` FK and no subcategories relation — use plain queryset.
article_cat_qs = ArticleCategory.objects.all()
book_cat_qs = BookCategory.objects.select_related("parent").prefetch_related(
    "subcategories"
)
dissertation_cat_qs = DissertationCategory.objects.select_related(
    "parent"
).prefetch_related("subcategories")


# Helper mixin to annotate queryset with is_bookmarked
class BookmarkAnnotateMixin:
    bookmark_field_name = None

    def annotate_bookmarks(self, queryset):
        if not self.bookmark_field_name:
            return queryset

        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            subquery = getattr(user.profile, self.bookmark_field_name).filter(
                pk=OuterRef("pk")
            )
            return queryset.annotate(is_bookmarked=Exists(subquery))

        return queryset.annotate(
            is_bookmarked=Value(False, output_field=BooleanField())
        )


# Helper to compute language counts across multiple models with few queries
def _aggregate_language_counts(models, languages=("tm", "ru", "en")):
    totals = {lang: 0 for lang in languages}
    for model in models:
        qs = model.objects.values("language").annotate(c=Count("id"))
        for r in qs:
            lang = r.get("language")
            if lang in totals:
                totals[lang] += r.get("c", 0)
    return totals


# Helper: merge top items from multiple models into a single sorted list
def _merge_top_items(
    models_with_labels, per_model=7, total_limit=8, fields=("id", "title", "views")
):
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


# Helper: build a date -> count map for one or more models using a date field
def _publication_counts_map(models, date_field, since_date):
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


def _daily_counts_list_from_map(counts_map, since_date, days=30, date_fmt="%Y-%m-%d"):
    dates = []
    counts = []
    for i in range(days):
        d = since_date + timedelta(days=i)
        dates.append(d.strftime(date_fmt))
        counts.append(counts_map.get(d, 0))
    return dates, counts


# Module-level Elasticsearch client and health helper
_ES_CLIENT = None


def get_es_client():
    global _ES_CLIENT
    if _ES_CLIENT is None:
        try:
            es_url = settings.ELASTICSEARCH_DSL["default"]["hosts"]
            _ES_CLIENT = Elasticsearch(es_url, timeout=30)
        except Exception:
            _ES_CLIENT = None
    return _ES_CLIENT


def es_ping_ok(client):
    ok = cache.get("es_ping_ok")
    if ok is None:
        try:
            ok = bool(client and client.ping())
        except Exception:
            ok = False
        cache.set("es_ping_ok", ok, 5)
    return ok


# ======================= СТАТЬИ =======================
@method_decorator(cache_page(60 * 10), name="list")
class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Article.objects.all()
        .order_by("-id")
        .prefetch_related(Prefetch("categories", queryset=article_cat_qs))
    )
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "type": ["exact"],
        "categories": ["exact"],
        "publication_date": ["gte", "lte", "exact"],
    }

    bookmark_field_name = "bookmarked_articles"

    def get_queryset(self):
        queryset = super().get_queryset()
        # For list action, avoid loading full `content` field which can be large
        if getattr(self, "action", None) == "list":
            queryset = queryset.only(
                "id",
                "title",
                "author",
                "average_rating",
                "rating_count",
                "views",
                "language",
            )
        # Do not annotate per-user `is_bookmarked` for list view to allow
        # shared caching across users (annotation is user-specific and
        # prevents cache hits under high concurrency).
        if getattr(self, "action", None) == "list":
            return queryset
        return BookmarkAnnotateMixin.annotate_bookmarks(self, queryset)

    def _get_cache_version(self):
        try:
            v = cache.get("content_cache_version")
            return int(v or 0)
        except Exception:
            return 0

        def get_serializer_class(self):
            if getattr(self, "action", None) == "list":
                return ArticleListSerializer
            return ArticleSerializer

    def retrieve(self, request, *args, **kwargs):
        """Cache per-object detail responses for a short time.

        Cache key includes user id to preserve `is_bookmarked` per-user.
        """
        pk = kwargs.get("pk")
        user_id = (
            request.user.id
            if getattr(request, "user", None) and request.user.is_authenticated
            else "anon"
        )
        cache_key = f"article:detail:v{self._get_cache_version()}:{pk}:user:{user_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        resp = super().retrieve(request, *args, **kwargs)
        try:
            cache.set(cache_key, resp.data, 60)
        except Exception:
            pass
        return resp


# ======================= КНИГИ =======================
@method_decorator(cache_page(60 * 10), name="list")
class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Book.objects.all()
        .order_by("-id")
        .prefetch_related(Prefetch("categories", queryset=book_cat_qs))
    )
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "categories": ["exact"],
    }

    bookmark_field_name = "bookmarked_books"

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, "action", None) == "list":
            queryset = queryset.only(
                "id",
                "title",
                "author",
                "average_rating",
                "rating_count",
                "views",
                "language",
            )
        if getattr(self, "action", None) == "list":
            return queryset
        return BookmarkAnnotateMixin.annotate_bookmarks(self, queryset)

    def _get_cache_version(self):
        try:
            v = cache.get("content_cache_version")
            return int(v or 0)
        except Exception:
            return 0

        def get_serializer_class(self):
            if getattr(self, "action", None) == "list":
                return BookListSerializer
            return BookSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        user_id = (
            request.user.id
            if getattr(request, "user", None) and request.user.is_authenticated
            else "anon"
        )
        cache_key = f"book:detail:v{self._get_cache_version()}:{pk}:user:{user_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        resp = super().retrieve(request, *args, **kwargs)
        try:
            cache.set(cache_key, resp.data, 60)
        except Exception:
            pass
        return resp


# ======================= ДИССЕРТАЦИИ =======================
@method_decorator(cache_page(60 * 10), name="list")
class DissertationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Dissertation.objects.all()
        .order_by("-id")
        .prefetch_related(Prefetch("categories", queryset=dissertation_cat_qs))
    )
    serializer_class = DissertationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "categories": ["exact"],
    }

    bookmark_field_name = "bookmarked_dissertations"

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, "action", None) == "list":
            queryset = queryset.only(
                "id",
                "title",
                "author",
                "average_rating",
                "rating_count",
                "views",
                "language",
            )
        if getattr(self, "action", None) == "list":
            return queryset
        return BookmarkAnnotateMixin.annotate_bookmarks(self, queryset)

    def _get_cache_version(self):
        try:
            v = cache.get("content_cache_version")
            return int(v or 0)
        except Exception:
            return 0

        def get_serializer_class(self):
            if getattr(self, "action", None) == "list":
                return DissertationListSerializer
            return DissertationSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        user_id = (
            request.user.id
            if getattr(request, "user", None) and request.user.is_authenticated
            else "anon"
        )
        cache_key = (
            f"dissertation:detail:v{self._get_cache_version()}:{pk}:user:{user_id}"
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        resp = super().retrieve(request, *args, **kwargs)
        try:
            cache.set(cache_key, resp.data, 60)
        except Exception:
            pass
        return resp


@method_decorator(cache_page(60 * 60), name="list")
class ArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticleCategory.objects.all().order_by("name")
    serializer_class = ArticleCategorySerializer
    pagination_class = None


@method_decorator(cache_page(60 * 60), name="list")
class BookCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        BookCategory.objects.all()
        .annotate(
            is_top_category=Case(
                When(parent__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .order_by("-is_top_category", "name")
    )
    serializer_class = BookCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"parent": ["exact", "isnull"]}
    pagination_class = None


@method_decorator(cache_page(60 * 60), name="list")
class DissertationCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        DissertationCategory.objects.all()
        .annotate(
            is_top_category=Case(
                When(parent__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .order_by("-is_top_category", "name")
    )
    serializer_class = DissertationCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"parent": ["exact", "isnull"]}
    pagination_class = None


# ============Registraion============


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


# ============Bookmark_Add============


class ToggleBookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        content_type = (request.data.get("type") or "").strip().lower()

        mapping = {
            "article": (Article, "bookmarked_articles"),
            "book": (Book, "bookmarked_books"),
            "dissertation": (Dissertation, "bookmarked_dissertations"),
        }

        if content_type not in mapping:
            return Response(
                {"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST
            )

        model, field_name = mapping[content_type]
        try:
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return Response(
                {"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND
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


# ============Bookmarks============
class UserBookmarksView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        # Cache per-user bookmarks for a short duration to reduce DB/serialization pressure
        cache_key = f"user_bookmarks:{request.user.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        articles_qs = (
            profile.bookmarked_articles.all()
            .prefetch_related(Prefetch("categories", queryset=article_cat_qs))
            .only("id", "title", "author", "average_rating", "rating_count", "views")
        )
        books_qs = (
            profile.bookmarked_books.all()
            .prefetch_related(Prefetch("categories", queryset=book_cat_qs))
            .only("id", "title", "author", "average_rating", "rating_count", "views")
        )
        dissertations_qs = (
            profile.bookmarked_dissertations.all()
            .prefetch_related(Prefetch("categories", queryset=dissertation_cat_qs))
            .only("id", "title", "author", "average_rating", "rating_count", "views")
        )

        data = {
            "articles": ArticleSerializer(
                articles_qs, many=True, context={"request": request}
            ).data,
            "books": BookSerializer(
                books_qs, many=True, context={"request": request}
            ).data,
            "dissertations": DissertationSerializer(
                dissertations_qs, many=True, context={"request": request}
            ).data,
        }

        try:
            cache.set(cache_key, data, 30)
        except Exception:
            pass

        return Response(data)


logger = logging.getLogger(__name__)


class ContentSearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
        from_ = (page - 1) * page_size

        # Try cache first (cache key includes full path with querystring and global cache version)
        try:
            version = int(cache.get("content_cache_version") or 0)
        except Exception:
            version = 0

        cache_key = f"search:v{version}:{request.get_full_path()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        # Подключение к Elasticsearch (модульный клиент)
        client = get_es_client()
        if not es_ping_ok(client):
            return Response({"error": "Elasticsearch недоступен"}, status=503)

        # Базовый запрос
        body = {
            "from": from_,
            "size": page_size,
            "query": {"bool": {"must": [], "filter": []}},
            # Limit returned source fields to reduce payload size
            "_source": [
                "title",
                "author",
                "language",
                "average_rating",
                "rating_count",
                "views",
                "publication_date",
                "image",
                "epub_file",
                "cover_image",
                "source_name",
                "source_url",
                "newspaper_or_journal",
                "author_workplace",
                "type",
                "categories",
            ],
            "highlight": {
                "pre_tags": ["<b class='highlight'>"],
                "post_tags": ["</b>"],
                "fields": {
                    "title": {"fragment_size": 100, "number_of_fragments": 1},
                    "content": {"fragment_size": 120, "number_of_fragments": 1},
                },
            },
            "sort": [{"_score": {"order": "desc"}}],
        }

        # Поисковый запрос
        if q:
            body["query"]["bool"]["must"].append(
                {
                    "multi_match": {
                        "query": q,
                        "fields": [
                            "title^10",
                            "content^3",
                            "author^5",
                            "author_workplace^2",
                            "source_name^2",
                            "newspaper_or_journal^2",
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            )
        else:
            body["query"]["bool"]["must"].append({"match_all": {}})

        # === ФИЛЬТРЫ ===
        filters = []

        # Тип контента: article, book, dissertation
        content_type = request.query_params.get("content_type")
        if content_type in ["article", "book", "dissertation"]:
            filters.append({"term": {"_index": f"{content_type}s"}})

        # Язык
        if request.query_params.get("language"):
            filters.append(
                {"term": {"language.keyword": request.query_params["language"]}}
            )

        # Только для статей
        if request.query_params.get("type"):
            filters.append({"term": {"type.keyword": request.query_params["type"]}})

        # Автор (точное совпадение)
        if request.query_params.get("author"):
            filters.append({"term": {"author.keyword": request.query_params["author"]}})

        # Дата публикации (точная)
        if request.query_params.get("publication_date"):
            filters.append(
                {"term": {"publication_date": request.query_params["publication_date"]}}
            )

        # Диапазон дат
        if request.query_params.get("publication_date__gte"):
            filters.append(
                {
                    "range": {
                        "publication_date": {
                            "gte": request.query_params["publication_date__gte"]
                        }
                    }
                }
            )
        if request.query_params.get("publication_date__lte"):
            filters.append(
                {
                    "range": {
                        "publication_date": {
                            "lte": request.query_params["publication_date__lte"]
                        }
                    }
                }
            )

        # Категории
        if request.query_params.get("category_id"):
            filters.append(
                {
                    "nested": {
                        "path": "categories",
                        "query": {
                            "term": {
                                "categories.id": int(
                                    request.query_params["category_id"]
                                )
                            }
                        },
                    }
                }
            )
        if request.query_params.get("category_name"):
            filters.append(
                {
                    "nested": {
                        "path": "categories",
                        "query": {
                            "match": {
                                "categories.name": request.query_params["category_name"]
                            }
                        },
                    }
                }
            )

        if filters:
            body["query"]["bool"]["filter"] = filters

        if not q and not content_type:
            body["sort"].insert(0, {"average_rating": {"order": "desc"}})
            body["sort"].append({"views": {"order": "desc"}})

        try:
            response = client.search(index="articles,books,dissertations", body=body)
        except Exception as e:
            logger.error(f"Elasticsearch error: {e}")
            return Response({"error": "Ошибка поиска"}, status=500)

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            index_name = hit["_index"]
            content_type = index_name.rstrip("s")

            base = {
                "id": int(hit["_id"]),
                "content_type": content_type,
                "title": source.get("title", "Без названия"),
                "author": source.get("author", "Неизвестен"),
                "language": source.get("language", "tm"),
                "type": source.get("type", "Неизвестен"),
                "average_rating": round(float(source.get("average_rating", 0)), 2),
                "rating_count": source.get("rating_count", 0),
                "views": source.get("views", 0),
                "score": hit.get("_score", 0),
                "highlight": hit.get("highlight", {}),
            }

            # Тип-специфичные поля
            if content_type == "article":
                base.update(
                    {
                        "author_workplace": source.get("author_workplace"),
                        "type": source.get("type"),
                        "publication_date": self._format_date(
                            source.get("publication_date")
                        ),
                        "source_name": source.get("source_name"),
                        "source_url": source.get("source_url"),
                        "newspaper_or_journal": source.get("newspaper_or_journal"),
                        "image": source.get("image"),
                    }
                )
            elif content_type == "book":
                base.update(
                    {
                        "epub_file": source.get("epub_file"),
                        "cover_image": source.get("cover_image"),
                    }
                )
            elif content_type == "dissertation":
                base.update(
                    {
                        "author_workplace": source.get("author_workplace"),
                        "publication_date": self._format_date(
                            source.get("publication_date")
                        ),
                    }
                )

            # Категории всегда
            base["categories"] = source.get("categories", [])

            results.append(base)

        resp_data = {
            "count": response["hits"]["total"]["value"],
            "page": page,
            "page_size": page_size,
            "has_next": len(results) == page_size,
            "results": results,
            "query": q,
        }

        # Cache search result for a short time (include version in key)
        try:
            cache.set(cache_key, resp_data, 300)
        except Exception:
            pass

        return Response(resp_data)

    @staticmethod
    def _format_date(date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").strftime(
                "%d.%m.%Y"
            )
        except Exception:
            return date_str.split("T")[0]


class RegisterViewHit(APIView):
    """Endpoint to register a view for a content object.

    Uses a cookie/session dedupe (24h) and writes to PendingView buffer.
    """

    def post(self, request, content_type, pk):
        content_type = (content_type or "").strip().lower()
        if content_type not in ("article", "book", "dissertation"):
            return Response({"error": "Invalid content_type"}, status=400)

        # Determine identifier: user or session
        now = timezone.now()
        ttl_hours = 24
        cutoff = now - timedelta(hours=ttl_hours)

        try:
            if request.user.is_authenticated:
                # Check recent record for this user
                seen = ViewRecord.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    content_id=pk,
                    last_seen__gte=cutoff,
                ).exists()
                if seen:
                    return Response(
                        {"accepted": False, "reason": "already_counted"}, status=200
                    )

                # create/update record
                ViewRecord.objects.update_or_create(
                    user=request.user,
                    content_type=content_type,
                    content_id=pk,
                    defaults={"last_seen": now},
                )
            else:
                # ensure session present
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
                        {"accepted": False, "reason": "already_counted"}, status=200
                    )

                ViewRecord.objects.update_or_create(
                    session_key=sk,
                    content_type=content_type,
                    content_id=pk,
                    defaults={"last_seen": now},
                )

            # increment pending buffer
            pv, created = PendingView.objects.get_or_create(
                content_type=content_type, content_id=pk, defaults={"count": 1}
            )
            if not created:
                PendingView.objects.filter(pk=pv.pk).update(count=F("count") + 1)

        except Exception:
            return Response({"error": "DB error"}, status=500)

        return Response({"accepted": True})


# ============Ratings============
class RateContentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["content_type", "content_id", "rating"],
            properties={
                "content_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["article", "book", "dissertation"],
                    description="",
                ),
                "content_id": openapi.Schema(type=openapi.TYPE_INTEGER, description=""),
                "rating": openapi.Schema(
                    type=openapi.TYPE_INTEGER, enum=[1, 2, 3, 4, 5], description=""
                ),
            },
            example={"content_type": "book", "content_id": 5, "rating": 5},
        ),
        security=[{"Bearer": []}],
        tags=["content_rating"],
    )
    def post(self, request):
        # ВСЁ БЕРЁМ ТОЛЬКО ИЗ request.data — никогда из request.content_id!
        content_type = request.data.get("content_type", "").strip().lower()
        content_id_str = request.data.get("content_id")
        rating_str = request.data.get("rating")

        # Проверяем наличие всех полей
        if not all([content_type, content_id_str, rating_str]):
            return Response(
                {"error": "content_type, content_id и rating обязательны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if content_type not in ["article", "book", "dissertation"]:
            return Response(
                {"error": "content_type должен быть: article, book или dissertation"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            content_id = int(content_id_str)
            rating = int(rating_str)
        except (ValueError, TypeError):
            return Response(
                {"error": "content_id и rating должны быть числами"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not 1 <= rating <= 5:
            return Response(
                {"error": "rating должен быть от 1 до 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model_map = {
            "article": Article,
            "book": Book,
            "dissertation": Dissertation,
        }
        model = model_map[content_type]

        try:
            obj = model.objects.get(id=content_id)
        except model.DoesNotExist:
            return Response(
                {"error": "Материал не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        rating_obj, created = ContentRating.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            content_id=content_id,
            defaults={"rating": rating},
        )

        ratings_qs = ContentRating.objects.filter(
            content_type=content_type, content_id=content_id
        )
        avg = ratings_qs.aggregate(avg=Avg("rating"))["avg"] or 0.0
        count = ratings_qs.count()

        obj.average_rating = round(float(avg), 2)
        obj.rating_count = count
        obj.save(update_fields=["average_rating", "rating_count"])

        return Response(
            {
                "message": "Sag boluň! Bahanyz kabul edildi.",
                "average_rating": obj.average_rating,
                "rating_count": obj.rating_count,
                "your_rating": rating,
            },
            status=status.HTTP_200_OK,
        )


@staff_member_required
def admin_statistics(request):
    # Try cached context first
    cached_ctx = cache.get("admin_statistics")
    if cached_ctx is not None:
        return render(request, "admin/statistics.html", cached_ctx)

    today = timezone.now()
    last_month = today - timedelta(days=30)
    last_week = today - timedelta(days=7)

    # ---- FIX: корректный подсчёт закладок ----
    bookmark_stats = Profile.objects.annotate(
        total_articles=Count("bookmarked_articles"),
        total_books=Count("bookmarked_books"),
        total_dissertations=Count("bookmarked_dissertations"),
    ).aggregate(
        articles=Sum("total_articles"),
        books=Sum("total_books"),
        dissertations=Sum("total_dissertations"),
    )

    # ---- FIX: корректное суммирование total_views ----
    total_views = (
        (Article.objects.aggregate(v=Sum("views"))["v"] or 0)
        + (Book.objects.aggregate(v=Sum("views"))["v"] or 0)
        + (Dissertation.objects.aggregate(v=Sum("views"))["v"] or 0)
    )

    # ---- AVG rating ----
    avg_article = Article.objects.aggregate(a=Avg("average_rating"))["a"] or 0
    avg_book = Book.objects.aggregate(a=Avg("average_rating"))["a"] or 0
    avg_dissertation = Dissertation.objects.aggregate(a=Avg("average_rating"))["a"] or 0

    avg_rating = round(
        (avg_article * 0.4) + (avg_book * 0.3) + (avg_dissertation * 0.3), 2
    )

    # compute counts once
    article_count = Article.objects.count()
    book_count = Book.objects.count()
    dissertation_count = Dissertation.objects.count()

    lang_totals = _aggregate_language_counts([Article, Book, Dissertation])
    tm_count = lang_totals.get("tm", 0)
    ru_count = lang_totals.get("ru", 0)
    en_count = lang_totals.get("en", 0)

    context = {
        "today": today.strftime("%Y-%m-%d %H:%M"),
        "total_materials": article_count + book_count + dissertation_count,
        "total_articles": article_count,
        "total_books": book_count,
        "total_dissertations": dissertation_count,
        "total_views": total_views,
        "total_users": User.objects.count(),
        "active_last_week": Profile.objects.filter(
            user__last_login__gte=last_week
        ).count(),
        "bookmarks_articles": bookmark_stats["articles"] or 0,
        "bookmarks_books": bookmark_stats["books"] or 0,
        "bookmarks_dissertations": bookmark_stats["dissertations"] or 0,
        "avg_rating": avg_rating,
        "avg_article_rating": round(avg_article, 2),
        "avg_book_rating": round(avg_book, 2),
        "avg_dissertation_rating": round(avg_dissertation, 2),
        "bookmarks_total": (
            (bookmark_stats["articles"] or 0)
            + (bookmark_stats["books"] or 0)
            + (bookmark_stats["dissertations"] or 0)
        ),
        "tm_count": tm_count,
        "ru_count": ru_count,
        "en_count": en_count,
        "top_articles": list(
            Article.objects.order_by("-views").only("id", "title", "views")[:5]
        ),
        "top_books": list(
            Book.objects.order_by("-views").only("id", "title", "views")[:5]
        ),
        "top_dissertations": list(
            Dissertation.objects.order_by("-views").only("id", "title", "views")[:5]
        ),
        # Only Article and Dissertation have `publication_date`; Book does not.
        "new_last_month": (
            Article.objects.filter(publication_date__gte=last_month).count()
            + Dissertation.objects.filter(publication_date__gte=last_month).count()
        ),
    }

    # language distribution (counts + percentages for static display)
    lang_counts = {"tm": tm_count, "ru": ru_count, "en": en_count}
    total_lang = sum(lang_counts.values())
    if total_lang:
        lang_percent = {
            k: round((v / total_lang) * 100, 1) for k, v in lang_counts.items()
        }
    else:
        lang_percent = {k: 0 for k in lang_counts}

    context.update(
        {"language_distribution": lang_counts, "language_percent": lang_percent}
    )

    # Per-model stats to display grouped sections in template
    article_stats = {
        "count": Article.objects.count(),
        "avg_rating": round(
            Article.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2
        ),
        "total_views": Article.objects.aggregate(v=Sum("views"))["v"] or 0,
        "top": list(
            Article.objects.order_by("-views").only("id", "title", "views")[:7]
        ),
        "new_last_month": Article.objects.filter(
            publication_date__gte=last_month
        ).count(),
    }

    book_stats = {
        "count": Book.objects.count(),
        "avg_rating": round(
            Book.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2
        ),
        "total_views": Book.objects.aggregate(v=Sum("views"))["v"] or 0,
        "top": list(Book.objects.order_by("-views").only("id", "title", "views")[:7]),
        # Book model has no publication_date; new_last_month not available
        "new_last_month": None,
    }

    dissertation_stats = {
        "count": Dissertation.objects.count(),
        "avg_rating": round(
            Dissertation.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2
        ),
        "total_views": Dissertation.objects.aggregate(v=Sum("views"))["v"] or 0,
        "top": list(
            Dissertation.objects.order_by("-views").only("id", "title", "views")[:7]
        ),
        "new_last_month": Dissertation.objects.filter(
            publication_date__gte=last_month
        ).count(),
    }

    context.update(
        {
            "article_stats": article_stats,
            "book_stats": book_stats,
            "dissertation_stats": dissertation_stats,
        }
    )

    # Cache the computed context for a short time
    try:
        cache.set("admin_statistics", context, 300)
    except Exception:
        pass

    return render(request, "admin/statistics.html", context)


@staff_member_required
def admin_statistics_data(request):
    """JSON endpoint with enhanced statistics for admin dashboard (used by frontend charts)."""
    # Try cached first
    cached = cache.get("admin_statistics_data")
    if cached is not None:
        return JsonResponse(cached)

    today = timezone.now().date()
    last_30 = today - timedelta(days=29)

    # Basic totals (reuse some of the calculations from admin_statistics)
    total_articles = Article.objects.count()
    total_books = Book.objects.count()
    total_dissertations = Dissertation.objects.count()

    total_views = (
        (Article.objects.aggregate(v=Sum("views"))["v"] or 0)
        + (Book.objects.aggregate(v=Sum("views"))["v"] or 0)
        + (Dissertation.objects.aggregate(v=Sum("views"))["v"] or 0)
    )

    # Language distribution
    lang_counts = _aggregate_language_counts([Article, Book, Dissertation])

    # Ratings distribution (1..5) — optimized single-query aggregation
    ratings_agg = ContentRating.objects.aggregate(
        r1=Sum(Case(When(rating=1, then=1), output_field=IntegerField())),
        r2=Sum(Case(When(rating=2, then=1), output_field=IntegerField())),
        r3=Sum(Case(When(rating=3, then=1), output_field=IntegerField())),
        r4=Sum(Case(When(rating=4, then=1), output_field=IntegerField())),
        r5=Sum(Case(When(rating=5, then=1), output_field=IntegerField())),
    )
    ratings = {
        "1": ratings_agg.get("r1") or 0,
        "2": ratings_agg.get("r2") or 0,
        "3": ratings_agg.get("r3") or 0,
        "4": ratings_agg.get("r4") or 0,
        "5": ratings_agg.get("r5") or 0,
    }

    # Top items (combine few top from each model)
    top_list = _merge_top_items(
        [(Article, "article"), (Book, "book"), (Dissertation, "dissertation")],
        per_model=7,
        total_limit=8,
    )

    # New items per day (articles + dissertations) for last 30 days
    counts_map = _publication_counts_map(
        [Article, Dissertation], "publication_date", last_30
    )
    dates, counts = _daily_counts_list_from_map(
        counts_map, last_30, days=30, date_fmt="%Y-%m-%d"
    )

    data = {
        "totals": {
            "total_materials": total_articles + total_books + total_dissertations,
            "total_articles": total_articles,
            "total_books": total_books,
            "total_dissertations": total_dissertations,
            "total_views": total_views,
            "total_users": User.objects.count(),
        },
        "language_distribution": lang_counts,
        "ratings_distribution": ratings,
        "top_items": top_list,
        "new_items": {"dates": dates, "counts": counts},
        "generated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        cache.set("admin_statistics_data", data, 120)
    except Exception:
        pass

    return JsonResponse(data)


@staff_member_required
def admin_chart(request, chart_name, fmt="svg"):
    """Render a chart server-side and return SVG (fmt currently supports only 'svg').

    chart_name: one of 'lang', 'ratings', 'new', 'top'
    """
    fmt = (fmt or "svg").lower()
    if fmt != "svg":
        return HttpResponse("Only svg supported", status=400)

    cache_key = f"chart:{chart_name}:svg"
    cached = cache.get(cache_key)
    if cached:
        return HttpResponse(cached, content_type="image/svg+xml")

    # import matplotlib lazily to avoid startup cost
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return HttpResponse("Matplotlib not available", status=500)

    fig = plt.Figure(figsize=(6, 4), dpi=100)
    ax = fig.subplots()

    if chart_name == "lang":
        lang_counts_chart = _aggregate_language_counts([Article, Book, Dissertation])
        vals = [
            lang_counts_chart.get("tm", 0),
            lang_counts_chart.get("ru", 0),
            lang_counts_chart.get("en", 0),
        ]
        labels = ["TM", "RU", "EN"]
        colors = ["#10b981", "#3b82f6", "#7c3aed"]
        ax.pie(
            vals,
            labels=labels,
            colors=colors,
            autopct=lambda p: f"{int(round(p * sum(vals) / 100))}",
            startangle=90,
        )
        ax.set_title("Language distribution")

    elif chart_name == "ratings":
        agg = ContentRating.objects.aggregate(
            r1=Sum(Case(When(rating=1, then=1), output_field=IntegerField())),
            r2=Sum(Case(When(rating=2, then=1), output_field=IntegerField())),
            r3=Sum(Case(When(rating=3, then=1), output_field=IntegerField())),
            r4=Sum(Case(When(rating=4, then=1), output_field=IntegerField())),
            r5=Sum(Case(When(rating=5, then=1), output_field=IntegerField())),
        )
        vals = [
            agg.get("r1") or 0,
            agg.get("r2") or 0,
            agg.get("r3") or 0,
            agg.get("r4") or 0,
            agg.get("r5") or 0,
        ]
        labels = ["1", "2", "3", "4", "5"]
        ax.bar(
            labels, vals, color=["#ef4444", "#f97316", "#f59e0b", "#10b981", "#3b82f6"]
        )
        ax.set_title("Ratings distribution")
        ax.set_ylabel("Count")

    elif chart_name == "new":
        today = timezone.now().date()
        last_30 = today - timedelta(days=29)
        counts_map = _publication_counts_map(
            [Article, Dissertation], "publication_date", last_30
        )
        dates, counts = _daily_counts_list_from_map(
            counts_map, last_30, days=30, date_fmt="%m-%d"
        )
        ax.plot(dates, counts, color="#3b82f6")
        ax.set_title("New items (last 30 days)")
        ax.set_xticks(dates[::5])
        ax.set_ylabel("Count")
        plt = matplotlib.pyplot
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    elif chart_name == "top":
        top_items = _merge_top_items(
            [(Article, "article"), (Book, "book"), (Dissertation, "dissertation")],
            per_model=5,
            total_limit=8,
            fields=("title", "views"),
        )
        labels = [
            t["title"][:40] + ("…" if len(t["title"]) > 40 else "") for t in top_items
        ]
        vals = [t["views"] for t in top_items]
        ax.barh(range(len(vals))[::-1], vals, color="#3b82f6")
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels[::-1])
        ax.set_title("Top materials by views")

    # small sparklines
    elif chart_name == "spark_new":
        # small sparkline for new items (last 30 days)
        today = timezone.now().date()
        last_30 = today - timedelta(days=29)
        counts_map = _publication_counts_map(
            [Article, Dissertation], "publication_date", last_30
        )
        _, counts = _daily_counts_list_from_map(
            counts_map, last_30, days=30, date_fmt="%Y-%m-%d"
        )
        ax.plot(counts, color="#3b82f6", linewidth=1)
        ax.axis("off")
        fig.set_size_inches(3, 0.6)

    elif chart_name == "spark_ratings":
        # small sparkline for ratings counts over 1..5 (horizontal bar simplified)
        agg = ContentRating.objects.aggregate(
            r1=Sum(Case(When(rating=1, then=1), output_field=IntegerField())),
            r2=Sum(Case(When(rating=2, then=1), output_field=IntegerField())),
            r3=Sum(Case(When(rating=3, then=1), output_field=IntegerField())),
            r4=Sum(Case(When(rating=4, then=1), output_field=IntegerField())),
            r5=Sum(Case(When(rating=5, then=1), output_field=IntegerField())),
        )
        vals = [
            agg.get("r1") or 0,
            agg.get("r2") or 0,
            agg.get("r3") or 0,
            agg.get("r4") or 0,
            agg.get("r5") or 0,
        ]
        ax.bar(range(len(vals)), vals, color="#10b981")
        ax.axis("off")
        fig.set_size_inches(3, 0.6)

    elif chart_name == "spark_users":
        # user registrations per day last 30
        today = timezone.now().date()
        last_30 = today - timedelta(days=29)
        # aggregate user registrations by date to avoid daily queries
        user_counts_qs = (
            User.objects.annotate(d=TruncDate("date_joined"))
            .filter(d__gte=last_30)
            .values("d")
            .annotate(c=Count("id"))
        )
        user_map = {r["d"]: r["c"] for r in user_counts_qs}
        counts = []
        for i in range(30):
            d = last_30 + timedelta(days=i)
            counts.append(user_map.get(d, 0))
        ax.plot(counts, color="#7c3aed", linewidth=1)
        ax.axis("off")
        fig.set_size_inches(3, 0.6)

    elif chart_name == "spark_top":
        # tiny horizontal bars for top items (views)
        top_items = _merge_top_items(
            [(Article, "article"), (Book, "book"), (Dissertation, "dissertation")],
            per_model=5,
            total_limit=6,
            fields=("title", "views"),
        )
        vals = [t["views"] for t in top_items]
        ax.bar(range(len(vals)), vals, color="#3b82f6")
        ax.axis("off")
        fig.set_size_inches(3, 0.6)

    else:
        return HttpResponse("Unknown chart", status=400)

    # render to SVG
    buf = BytesIO()
    try:
        fig.savefig(buf, format="svg", bbox_inches="tight")
        svg = buf.getvalue()
        cache.set(cache_key, svg, 300)
        return HttpResponse(svg, content_type="image/svg+xml")
    finally:
        buf.close()
