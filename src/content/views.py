from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Case, When, Value, IntegerField, Exists, OuterRef
from elasticsearch import Elasticsearch

from django.conf import settings
from datetime import datetime
from .models import (
    Article,
    Book,
    Dissertation,
    ArticleCategory,
    BookCategory,
    DissertationCategory,
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
            queryset = queryset.annotate(
                is_bookmarked=Exists(
                    User.objects.filter(
                        pk=self.request.user.pk, bookmarks_articles=OuterRef("pk")
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_bookmarked=Value(False, output_field=IntegerField())
            )
        return queryset


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
            queryset = queryset.annotate(
                is_bookmarked=Exists(
                    User.objects.filter(
                        pk=self.request.user.pk, bookmarks_books=OuterRef("pk")
                    )
                )
            )
        else:
            queryset = queryset.annotate(is_bookmarked=Value(False))
        return queryset


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
            queryset = queryset.annotate(
                is_bookmarked=Exists(
                    User.objects.filter(
                        pk=self.request.user.pk, bookmarks_dissertations=OuterRef("pk")
                    )
                )
            )
        else:
            queryset = queryset.annotate(is_bookmarked=Value(False))
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


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class ToggleBookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        content_type = request.data.get("type")

        if content_type == "article":
            model = Article
            field_name = "bookmarks_articles"
        elif content_type == "book":
            model = Book
            field_name = "bookmarks_books"
        elif content_type == "dissertation":
            model = Dissertation
            field_name = "bookmarks_dissertations"
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


class UserBookmarksView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile

        data = {
            "articles": ArticleSerializer(
                profile.bookmarks_articles.all(),
                many=True,
                context={"request": request},
            ).data,
            "books": BookSerializer(
                profile.bookmarks_books.all(), many=True, context={"request": request}
            ).data,
            "dissertations": DissertationSerializer(
                profile.bookmarks_dissertations.all(),
                many=True,
                context={"request": request},
            ).data,
        }
        return Response(data)


class ContentSearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        page = int(request.query_params.get("page", 1))
        page_size = getattr(settings, "REST_FRAMEWORK", {}).get("PAGE_SIZE")
        from_ = (page - 1) * page_size

        client = Elasticsearch(["http://127.0.0.1:9200"])

        body = {
            "from": from_,
            "size": page_size,
            "query": {"bool": {"must": []}},
            "highlight": {
                "fields": {
                    "title": {"fragment_size": 150},
                    "content": {"fragment_size": 200},
                }
            },
        }

        # Поиск
        if q:
            body["query"]["bool"]["must"].append(
                {
                    "multi_match": {
                        "query": q,
                        "fields": [
                            "title^5",
                            "content^2",
                            "author^3",
                            "author_workplace",
                            "source_name",
                        ],
                        "info_type": "best_fields",
                    }
                }
            )
        else:
            body["query"]["bool"]["must"].append({"match_all": {}})

        # Фильтры
        filters = []
        if request.query_params.get("info_type"):
            filters.append(
                {"term": {"_index": request.query_params["info_type"] + "s"}}
            )
        if request.query_params.get("language"):
            filters.append({"term": {"language": request.query_params["language"]}})
        if request.query_params.get("type"):
            filters.append({"term": {"type": request.query_params["type"]}})
        if request.query_params.get("author"):
            filters.append({"term": {"author.keyword": request.query_params["author"]}})
        if request.query_params.get("publication_date"):
            filters.append(
                {"term": {"publication_date": request.query_params["publication_date"]}}
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

        if filters:
            body["query"]["bool"]["filter"] = filters

        # Выполняем поиск по всем индексам
        response = client.search(index="articles,books,dissertations", body=body)

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            index_type = hit["_index"].rstrip("s")

            # Общие поля
            base = {
                "id": int(hit["_id"]),
                "info_type": index_type,
                "title": source.get("title", "Без названия"),
                "author": source.get("author", "Автор не указан"),
                "language": source.get("language", ""),
                "rating": source.get("rating", 0),
                "views": source.get("views", 0),
                "score": hit.get("_score", 0),
            }

            # Специфичные поля
            if index_type == "article":
                base.update(
                    {
                        "content": source.get("content", ""),
                        "author_workplace": source.get("author_workplace", ""),
                        "type": source.get("type", ""),
                        "publication_date": (
                            datetime.strptime(
                                source["publication_date"], "%Y-%m-%d"
                            ).strftime("%d.%m.%Y")
                            if source.get("publication_date")
                            else None
                        ),
                        "source_name": source.get("source_name", ""),
                        "source_url": source.get("source_url", ""),
                        "newspaper_or_journal": source.get("newspaper_or_journal", ""),
                        "image": source.get("image", ""),
                        "categories": source.get("categories", []),
                    }
                )
            elif index_type == "book":
                base.update(
                    {
                        "content": source.get("content", ""),
                        "epub_file": source.get("epub_file", ""),
                        "cover_image": source.get("cover_image", ""),
                        "categories": source.get("categories", []),
                    }
                )
            elif index_type == "dissertation":
                base.update(
                    {
                        "content": source.get("content", ""),
                        "author_workplace": source.get("author_workplace", ""),
                        "publication_date": (
                            datetime.strptime(
                                source["publication_date"], "%Y-%m-%d"
                            ).strftime("%d.%m.%Y")
                            if source.get("publication_date")
                            else None
                        ),
                        "categories": source.get("categories", []),
                    }
                )

            if "highlight" in hit:
                base["highlight"] = hit["highlight"]

            results.append(base)

        return Response(
            {
                "count": response["hits"]["total"]["value"],
                "results": results,
                "page": page,
                "page_size": page_size,
            }
        )
