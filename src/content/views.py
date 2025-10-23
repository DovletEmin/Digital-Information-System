from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Article, Book, Dissertation,
    ArticleCategory, BookCategory, DissertationCategory
)
from .serializers import (
    ArticleSerializer, BookSerializer, DissertationSerializer,
    ArticleCategorySerializer, BookCategorySerializer, DissertationCategorySerializer
)

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'language': ['exact'],
        'type': ['exact'],
        'categories': ['exact'],
        'publication_date': ['gte', 'lte', 'exact'],
    }

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'language': ['exact'],
        'categories': ['exact'],
    }

class DissertationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dissertation.objects.all()
    serializer_class = DissertationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'language': ['exact'],
        'categories': ['exact'],
    }

class ArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticleCategory.objects.all()
    serializer_class = ArticleCategorySerializer

class BookCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookCategory.objects.all()
    serializer_class = BookCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'parent': ['exact', 'isnull'],
    }

class DissertationCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DissertationCategory.objects.all()
    serializer_class = DissertationCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'parent': ['exact', 'isnull'],
    }