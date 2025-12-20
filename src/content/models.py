from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator


# =============Categories=============
class ArticleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Article Categories"

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        unique_together = ("name", "parent")
        verbose_name_plural = "Book Categories"

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name


class DissertationCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        unique_together = ("name", "parent")
        verbose_name_plural = "Dissertation Categories"

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name


# =============User_Profile=============
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    bookmarked_articles = models.ManyToManyField(
        "Article", blank=True, related_name="bookmarked_by"
    )
    bookmarked_books = models.ManyToManyField(
        "Book", blank=True, related_name="bookmarked_by"
    )
    bookmarked_dissertations = models.ManyToManyField(
        "Dissertation", blank=True, related_name="bookmarked_by"
    )

    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)


# =============Content_Models=============
class Article(models.Model):
    LANGUAGE_CHOICES = [("tm", "Turkmen"), ("ru", "Russian"), ("en", "English")]
    TYPE_CHOICES = [("local", "Local"), ("foreign", "Foreign")]

    title = models.CharField(max_length=255)
    content = RichTextField()
    author = models.CharField(max_length=100)
    author_workplace = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    views = models.IntegerField(default=0)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="tm")
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default="local")
    publication_date = models.DateField()
    source_name = models.CharField(max_length=255, blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    newspaper_or_journal = models.CharField(max_length=255, blank=True, null=True)
    categories = models.ManyToManyField(
        ArticleCategory, related_name="articles", blank=True
    )
    image = models.ImageField(upload_to="books/article_images/", blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.language})"


class Book(models.Model):
    LANGUAGE_CHOICES = [("tm", "Turkmen"), ("ru", "Russian"), ("en", "English")]

    title = models.CharField(max_length=255)
    content = RichTextField(blank=True, null=True)
    epub_file = models.FileField(upload_to="books/epub/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="books/covers/", blank=True, null=True)
    author = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    views = models.IntegerField(default=0)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="tm")
    categories = models.ManyToManyField(BookCategory, related_name="books", blank=True)

    def __str__(self):
        return f"{self.title} ({self.author})"

    def save(self, *args, **kwargs):
        if not self.content and not self.epub_file:
            raise ValueError("Должно быть заполнено хотя бы content или epub_file.")
        super().save(*args, **kwargs)


class Dissertation(models.Model):
    LANGUAGE_CHOICES = [("tm", "Turkmen"), ("ru", "Russian"), ("en", "English")]

    title = models.CharField(max_length=255)
    content = RichTextField()
    author = models.CharField(max_length=100)
    author_workplace = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    views = models.IntegerField(default=0)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="tm")
    publication_date = models.DateField()
    categories = models.ManyToManyField(
        DissertationCategory, related_name="dissertations", blank=True
    )

    def __str__(self):
        return f"{self.title} ({self.author})"


# =============Rating=============
class ContentRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=20)
    content_id = models.PositiveIntegerField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content_type", "content_id")

    def __str__(self):
        return (
            f"{self.user} -> {self.content_id} {self.content_id}: {self.rating} stars"
        )


class PendingView(models.Model):
    CONTENT_CHOICES = [("article", "Article"), ("book", "Book"), ("dissertation", "Dissertation")]

    content_type = models.CharField(max_length=20, choices=CONTENT_CHOICES)
    content_id = models.PositiveIntegerField()
    count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("content_type", "content_id")

    def __str__(self):
        return f"PendingView {self.content_type}#{self.content_id} = {self.count}"
