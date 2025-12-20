from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Article,
    Book,
    Dissertation,
    ArticleCategory,
    BookCategory,
    DissertationCategory,
)


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ["id", "name"]


class BookCategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = BookCategory
        fields = ["id", "name", "parent", "subcategories"]

    def get_subcategories(self, obj):
        return [cat.id for cat in obj.subcategories.all()]


class DissertationCategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = DissertationCategory
        fields = ["id", "name", "parent", "subcategories"]

    def get_subcategories(self, obj):
        return [cat.id for cat in obj.subcategories.all()]


class ArticleSerializer(serializers.ModelSerializer):
    categories = ArticleCategorySerializer(many=True, read_only=True)
    is_bookmarked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_workplace",
            "average_rating",
            "rating_count",
            "views",
            "language",
            "type",
            "publication_date",
            "source_name",
            "source_url",
            "newspaper_or_journal",
            "categories",
            "image",
            "is_bookmarked",
        ]
        read_only_fields = fields

    def get_is_bookmarked(self, obj):
        # Removed DB lookup; `is_bookmarked` should be annotated on the queryset
        return getattr(obj, "is_bookmarked", False)


class BookSerializer(serializers.ModelSerializer):
    categories = BookCategorySerializer(many=True, read_only=True)
    is_bookmarked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "content",
            "epub_file",
            "cover_image",
            "author",
            "average_rating",
            "rating_count",
            "views",
            "language",
            "categories",
            "is_bookmarked",
        ]
        read_only_fields = fields

    def get_is_bookmarked(self, obj):
        return getattr(obj, "is_bookmarked", False)


class DissertationSerializer(serializers.ModelSerializer):
    categories = DissertationCategorySerializer(many=True, read_only=True)
    is_bookmarked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Dissertation
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_workplace",
            "average_rating",
            "rating_count",
            "views",
            "language",
            "publication_date",
            "categories",
            "is_bookmarked",
        ]
        read_only_fields = fields

    def get_is_bookmarked(self, obj):
        return getattr(obj, "is_bookmarked", False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user
