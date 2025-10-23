from django.db import models
from django.contrib.auth.models import User

class ArticleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Article Categories"

    def __str__(self):
        return self.name
    

class BookCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="subcategories")

    class Meta:
        unique_together = ('name', 'parent')
        verbose_name_plural = "Book Categories"


    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    

class DissertationCategory(models.Model):
    name = models.CharField(max_length = 100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        unique_together = ('name', 'parent')
        verbose_name_plural = "Dissertation Categories"

    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    

class Article(models.Model):
    LANGUAGE_CHOICES = [
        ('tm', 'Turkmen'),
        ('ru', 'Russian'),
        ('en', 'English'),
    ]

    TYPE_CHOICES = [
        ('local', 'Local'),
        ('foreign', 'Foreign'),
    ]

    title = models.CharField(max_length = 255)
    content = models.TextField()
    author = models.CharField(max_length=100)
    author_workplace = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(default=0.0)
    views = models.IntegerField(default=0)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_articles', blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='tm')
    type = models.CharField(max_length=7,choices=TYPE_CHOICES, default='local')
    publication_date = models.DateField()
    source_name = models.CharField(max_length=255, blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    newspaper_or_journal = models.CharField(max_length=255, blank=True, null=True)
    categories = models.ManyToManyField(ArticleCategory, related_name='articles', blank=True)

    def __str__(self):
        return f"{self.title} > {self.author} > {self.language} > {self.categories}"


class Book(models.Model):
    LANGUAGE_CHOICES = [
        ('tm', 'Turkmen'),
        ('ru', 'Russian'),
        ('en', 'English'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    epub_file = models.FileField(upload_to='books/epub/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True)
    author = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    views = models.IntegerField(default=0)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='tm')
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_books', blank=True)
    categories = models.ManyToManyField(BookCategory, related_name='books', blank=True)

    def __str__(self):
        return f"{self.title} > {self.author} > {self.language} > {self.categories}"
    
    def save(self, *args, **kwargs):
        if not self.content and not self.epub_file:
            raise ValueError("Должно быть заполнено хотя бы content или epub_file.")
        super().save(*args, **kwargs)


class Dissertation(models.Model):
    LANGUAGE_CHOICES = [
        ('tm', 'Turkmen'),
        ('rm', 'Russian'),
        ('en', 'English'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=100)
    author_workplace = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(default=0.0)
    views = models.IntegerField(default=0)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_dissertations', blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='tm')
    publication_date = models.DateField()
    categories = models.ManyToManyField(DissertationCategory, related_name='dissertations', blank=True)

    def __str__(self):
        return f"{self.title} > {self.author} > {self.language} > {self.categories}"