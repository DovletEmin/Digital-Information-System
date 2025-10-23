from django.contrib import admin
from .models import (
    Article, Book, Dissertation,
    ArticleCategory, BookCategory, DissertationCategory
)

admin.site.register(Article)
admin.site.register(Book)
admin.site.register(Dissertation)
admin.site.register(ArticleCategory)
admin.site.register(BookCategory)
admin.site.register(DissertationCategory)