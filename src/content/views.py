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
from django.db.models import Case, When, Value, IntegerField

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all().order_by('id')
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'language': ['exact'],
        'type': ['exact'],
        'categories': ['exact'],
        'publication_date': ['gte', 'lte', 'exact'],
    }

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'language': ['exact'],
        'categories': ['exact'],
    }

class DissertationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dissertation.objects.all().order_by('id')
    serializer_class = DissertationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'language': ['exact'],
        'categories': ['exact'],
    }

class ArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticleCategory.objects.all().order_by('name')
    serializer_class = ArticleCategorySerializer

class BookCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookCategory.objects.all().annotate(
        is_top_category=Case(
            When(parent__isnull=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-is_top_category', 'name') 
    serializer_class = BookCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'parent': ['exact', 'isnull'],
    }

class DissertationCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DissertationCategory.objects.all().annotate(
        is_top_category=Case(
            When(parent__isnull=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-is_top_category', 'name') 
    serializer_class = DissertationCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'parent': ['exact', 'isnull'],
    }