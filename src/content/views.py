from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import (
    Case,
    When,
    Value,
    IntegerField,
    Exists,
    OuterRef,
    BooleanField,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Avg

from .models import (
    Article,
    Book,
    Dissertation,
    ArticleCategory,
    BookCategory,
    DissertationCategory,
    ContentRating,
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
            # Проверяем, есть ли статья в профиле пользователя
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
