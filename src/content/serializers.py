from rest_framework import serializers
from .models import (
    Article, Book, Dissertation,
    ArticleCategory, BookCategory, DissertationCategory
)


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['id', 'name']


class BookCategorySeralizer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=BookCategory.objects.all(), allow_null=True)
    subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = BookCategory
        fields = ['id', 'name', 'parent', 'subcategories']


class DissertationCategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=DissertationCategory.objects.all(), allow_null=True)
    subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = DissertationCategory
        fields = ['id', 'name', 'parent', 'subcategories']


class ArticleSerializer(serializers.ModelSerializer):
    categories = ArticleCategorySerializer(many=True, read_only=True)
    bookmarks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_workplace', 'rating', 'views',
                  'language', 'type', 'publication_date', 'source_name', 'source_url',
                  'newspaper_or_journal', 'categories', 'bookmarks']