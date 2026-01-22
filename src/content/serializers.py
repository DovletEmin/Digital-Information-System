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


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "author",
            "average_rating",
            "rating_count",
            "views",
            "language",
            "image",
        ]
        read_only_fields = fields


class BookCategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = BookCategory
        fields = ["id", "name", "parent", "subcategories"]

    def get_subcategories(self, obj):
        # Use the prefetched cache when available to avoid extra queries.
        cache = getattr(obj, "_prefetched_objects_cache", None)
        if cache and "subcategories" in cache:
            return [cat.id for cat in cache["subcategories"]]
        return [cat.id for cat in obj.subcategories.all()]


class DissertationCategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = DissertationCategory
        fields = ["id", "name", "parent", "subcategories"]

    def get_subcategories(self, obj):
        cache = getattr(obj, "_prefetched_objects_cache", None)
        if cache and "subcategories" in cache:
            return [cat.id for cat in cache["subcategories"]]
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
    """
    User registration serializer with email validation and strong password enforcement.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirm")
        extra_kwargs = {
            "password": {"write_only": True},
            "password_confirm": {"write_only": True},
        }

    def validate_username(self, value):
        """Validate username is unique and follows rules"""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long."
            )

        if not value.replace("_", "").replace("-", "").isalnum():
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, underscores, and hyphens."
            )

        return value

    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, data):
        """Validate passwords match"""
        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop("password_confirm")  # Remove password_confirm
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "average_rating",
            "rating_count",
            "views",
            "language",
            "cover_image",
        ]
        read_only_fields = fields


class DissertationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dissertation
        fields = [
            "id",
            "title",
            "author",
            "average_rating",
            "rating_count",
            "views",
            "language",
            "publication_date",
        ]
        read_only_fields = fields
