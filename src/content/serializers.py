from rest_framework import serializers
from .models import (
    Article, Book, Dissertation,
    ArticleCategory, BookCategory, DissertationCategory
)


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['id', 'name']


class BookCategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = BookCategory
        fields = ['id', 'name', 'parent', 'subcategories']


class DissertationCategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
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
        read_only_fields = fields
        

class BookSerializer(serializers.ModelField):
    categories = BookCategorySerializer(many=True, read_only=True)
    bookmarks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    cover_image = serializers.ImageField(read_only=True)
    epub_file = serializers.FileField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'content', 'epub_file', 'cover_image', 'author',
                  'rating', 'views', 'language', 'categories', 'bookmarks']
        read_only_fields = fields


class DissertationSerializer(serializers.ModelField):
    categories = DissertationCategorySerializer(many=True, read_only=True)
    bookmarks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        models = Dissertation
        fields = ['id', 'title', 'content', 'author', 'author_workplace', 'rating',
                  'views', 'language', 'publication_date', 'categories', 'bookmarks']
        read_only_fields = fields