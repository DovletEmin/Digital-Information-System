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
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = BookCategory
        fields = ['id', 'name', 'parent', 'subcategories']

    def get_subcategories(self, obj):
        return [category.id for category in obj.subcategories.all()]

class DissertationCategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = DissertationCategory
        fields = ['id', 'name', 'parent', 'subcategories']

    def get_subcategories(self, obj):
        return [category.id for category in obj.subcategories.all()]

class ArticleSerializer(serializers.ModelSerializer):
    categories = ArticleCategorySerializer(many=True, read_only=True)
    bookmarks = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_workplace', 'rating', 'views',
                  'language', 'type', 'publication_date', 'source_name', 'source_url',
                  'newspaper_or_journal', 'categories', 'bookmarks', 'image']
        read_only_fields = fields

    def get_bookmarks(self, obj):
        return [user.id for user in obj.bookmarks.all()]

class BookSerializer(serializers.ModelSerializer):
    categories = BookCategorySerializer(many=True, read_only=True)
    bookmarks = serializers.SerializerMethodField()
    cover_image = serializers.ImageField(read_only=True)
    epub_file = serializers.FileField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'content', 'epub_file', 'cover_image', 'author',
                  'rating', 'views', 'language', 'categories', 'bookmarks']
        read_only_fields = fields

    def get_bookmarks(self, obj):
        return [user.id for user in obj.bookmarks.all()]

class DissertationSerializer(serializers.ModelSerializer):
    categories = DissertationCategorySerializer(many=True, read_only=True)
    bookmarks = serializers.SerializerMethodField()

    class Meta:
        model = Dissertation
        fields = ['id', 'title', 'content', 'author', 'author_workplace', 'rating',
                  'views', 'language', 'publication_date', 'categories', 'bookmarks']
        read_only_fields = fields

    def get_bookmarks(self, obj):
        return [user.id for user in obj.bookmarks.all()]