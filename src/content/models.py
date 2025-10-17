from django.db import models
from django.contrib.auth.models import User


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

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=100)
    author_workplace = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(default=0.0)
    views = models.IntegerField(default=0)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_articles', blank=True) 
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='tm')
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default='local')
    publication_date = models.DateField()
    source_name = models.CharField(max_length=255, blank=True, null=True)  
    source_url = models.URLField(blank=True, null=True) 
    newspaper_or_journal = models.CharField(max_length=255, blank=True, null=True)  
    
    def __str__(self):
        return self.title