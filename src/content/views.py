from rest_framework import viewsets
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
    filterset_fields = ['language', 'type', 'categories']


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_fields = ['language', 'categories']


class DissertationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dissertation.objects.all()
    serializer_class = DissertationSerializer
    filterset_fields = ['language', 'categories']