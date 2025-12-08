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
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render
import logging
import json
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
from .serializers import (
    ArticleSerializer,
    BookSerializer,
    DissertationSerializer,
    ArticleCategorySerializer,
    BookCategorySerializer,
    DissertationCategorySerializer,
    UserSerializer,
)


# ======================= СТАТЬИ =======================
class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all().order_by("-id")
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "type": ["exact"],
        "categories": ["exact"],
        "publication_date": ["gte", "lte", "exact"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            subquery = self.request.user.profile.bookmarked_articles.filter(
                pk=OuterRef("pk")
            )
            queryset = queryset.annotate(is_bookmarked=Exists(subquery))
        else:
            queryset = queryset.annotate(
                is_bookmarked=Value(False, output_field=BooleanField())
            )

        return queryset


# ======================= КНИГИ =======================
class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all().order_by("-id")
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "categories": ["exact"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            subquery = self.request.user.profile.bookmarked_books.filter(
                pk=OuterRef("pk")
            )
            queryset = queryset.annotate(is_bookmarked=Exists(subquery))
        else:
            queryset = queryset.annotate(
                is_bookmarked=Value(False, output_field=BooleanField())
            )

        return queryset


# ======================= ДИССЕРТАЦИИ =======================
class DissertationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dissertation.objects.all().order_by("-id")
    serializer_class = DissertationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "language": ["exact"],
        "categories": ["exact"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            subquery = self.request.user.profile.bookmarked_dissertations.filter(
                pk=OuterRef("pk")
            )
            queryset = queryset.annotate(is_bookmarked=Exists(subquery))
        else:
            queryset = queryset.annotate(
                is_bookmarked=Value(False, output_field=BooleanField())
            )

        return queryset


class ArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticleCategory.objects.all().order_by("name")
    serializer_class = ArticleCategorySerializer
    pagination_class = None


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
        content_type = request.data.get("type")

        if content_type == "article":
            model = Article
            field_name = "bookmarked_articles"
        elif content_type == "book":
            model = Book
            field_name = "bookmarked_books"
        elif content_type == "dissertation":
            model = Dissertation
            field_name = "bookmarked_dissertations"
        else:
            return Response(
                {"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST
            )

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

        data = {
            "articles": ArticleSerializer(
                profile.bookmarked_articles.all(),
                many=True,
                context={"request": request},
            ).data,
            "books": BookSerializer(
                profile.bookmarked_books.all(), many=True, context={"request": request}
            ).data,
            "dissertations": DissertationSerializer(
                profile.bookmarked_dissertations.all(),
                many=True,
                context={"request": request},
            ).data,
        }
        return Response(data)


logger = logging.getLogger(__name__)


class ContentSearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
        from_ = (page - 1) * page_size

        # Подключение к Elasticsearch
        es_url = settings.ELASTICSEARCH_DSL["default"]["hosts"]
        client = Elasticsearch(es_url, timeout=30)

        if not client.ping():
            return Response({"error": "Elasticsearch недоступен"}, status=503)

        # Базовый запрос
        body = {
            "from": from_,
            "size": page_size,
            "query": {"bool": {"must": [], "filter": []}},
            "highlight": {
                "pre_tags": ["<b class='highlight'>"],
                "post_tags": ["</b>"],
                "fields": {
                    "title": {"fragment_size": 150, "number_of_fragments": 1},
                    "content": {"fragment_size": 200, "number_of_fragments": 2},
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
        info_type = request.query_params.get("info_type")
        if info_type in ["article", "book", "dissertation"]:
            filters.append({"term": {"_index": f"{info_type}s"}})

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

        if not q and not info_type:
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

        return Response(
            {
                "count": response["hits"]["total"]["value"],
                "page": page,
                "page_size": page_size,
                "has_next": len(results) == page_size,
                "results": results,
                "query": q,
            }
        )

    def _format_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").strftime(
                "%d.%m.%Y"
            )
        except Exception:
            return date_str.split("T")[0]


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
    avg_rating = round(
        ((Article.objects.aggregate(a=Avg("average_rating"))["a"] or 0) * 0.4)
        + ((Book.objects.aggregate(a=Avg("average_rating"))["a"] or 0) * 0.3)
        + ((Dissertation.objects.aggregate(a=Avg("average_rating"))["a"] or 0) * 0.3),
        2,
    )

    context = {
        "today": today.strftime("%Y-%m-%d %H:%M"),
        "total_materials": (
            Article.objects.count()
            + Book.objects.count()
            + Dissertation.objects.count()
        ),
        "total_articles": Article.objects.count(),
        "total_books": Book.objects.count(),
        "total_dissertations": Dissertation.objects.count(),
        "total_views": total_views,
        "total_users": User.objects.count(),
        "active_last_week": Profile.objects.filter(
            user__last_login__gte=last_week
        ).count(),
        "bookmarks_articles": bookmark_stats["articles"] or 0,
        "bookmarks_books": bookmark_stats["books"] or 0,
        "bookmarks_dissertations": bookmark_stats["dissertations"] or 0,
        "avg_rating": avg_rating,
        "avg_article_rating": round(Article.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2),
        "avg_book_rating": round(Book.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2),
        "avg_dissertation_rating": round(Dissertation.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2),
        "bookmarks_total": (
            (bookmark_stats["articles"] or 0)
            + (bookmark_stats["books"] or 0)
            + (bookmark_stats["dissertations"] or 0)
        ),
        "tm_count": (
            Article.objects.filter(language="tm").count()
            + Book.objects.filter(language="tm").count()
            + Dissertation.objects.filter(language="tm").count()
        ),
        "ru_count": (
            Article.objects.filter(language="ru").count()
            + Book.objects.filter(language="ru").count()
            + Dissertation.objects.filter(language="ru").count()
        ),
        "en_count": (
            Article.objects.filter(language="en").count()
            + Book.objects.filter(language="en").count()
            + Dissertation.objects.filter(language="en").count()
        ),
        "top_articles": Article.objects.order_by("-views")[:5],
        "top_books": Book.objects.order_by("-views")[:5],
        "top_dissertations": Dissertation.objects.order_by("-views")[:5],
        # Only Article and Dissertation have `publication_date`; Book does not.
        "new_last_month": (
            Article.objects.filter(publication_date__gte=last_month).count()
            + Dissertation.objects.filter(publication_date__gte=last_month).count()
        ),
    }

    # language distribution (counts + percentages for static display)
    lang_counts = {
        "tm": context["tm_count"],
        "ru": context["ru_count"],
        "en": context["en_count"],
    }
    total_lang = sum(lang_counts.values())
    if total_lang:
        lang_percent = {k: round((v / total_lang) * 100, 1) for k, v in lang_counts.items()}
    else:
        lang_percent = {k: 0 for k in lang_counts}

    context.update(
        {
            "language_distribution": lang_counts,
            "language_percent": lang_percent,
        }
    )

    # Per-model stats to display grouped sections in template
    article_stats = {
        "count": Article.objects.count(),
        "avg_rating": round(Article.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2),
        "total_views": Article.objects.aggregate(v=Sum("views"))["v"] or 0,
        "top": list(Article.objects.order_by("-views")[:7]),
        "new_last_month": Article.objects.filter(publication_date__gte=last_month).count(),
    }

    book_stats = {
        "count": Book.objects.count(),
        "avg_rating": round(Book.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2),
        "total_views": Book.objects.aggregate(v=Sum("views"))["v"] or 0,
        "top": list(Book.objects.order_by("-views")[:7]),
        # Book model has no publication_date; new_last_month not available
        "new_last_month": None,
    }

    dissertation_stats = {
        "count": Dissertation.objects.count(),
        "avg_rating": round(Dissertation.objects.aggregate(a=Avg("average_rating"))["a"] or 0, 2),
        "total_views": Dissertation.objects.aggregate(v=Sum("views"))["v"] or 0,
        "top": list(Dissertation.objects.order_by("-views")[:7]),
        "new_last_month": Dissertation.objects.filter(publication_date__gte=last_month).count(),
    }

    context.update({
        "article_stats": article_stats,
        "book_stats": book_stats,
        "dissertation_stats": dissertation_stats,
    })

    return render(request, "admin/statistics.html", context)
