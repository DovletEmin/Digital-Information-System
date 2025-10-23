from django.contrib import admin
from .models import (
    Article, Book, Dissertation,
    ArticleCategory, BookCategory, DissertationCategory
)

def get_categories(obj):
    return ", ".join([category.name for category in obj.categories.all()])

get_categories.short_description = 'Категории'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'language', 'get_categories', 'publication_date')
    list_filter = ('language', 'type', 'categories')
    search_fields = ('title', 'author', 'content')
    list_per_page = 25

    def get_categories(self, obj):
        return get_categories(obj)
    get_categories.short_description = 'Категории'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'language', 'get_categories', 'rating', 'views')
    list_filter = ('language', 'categories')
    search_fields = ('title', 'author', 'content')
    list_per_page = 25

    def get_categories(self, obj):
        return get_categories(obj)
    get_categories.short_description = 'Категории'

@admin.register(Dissertation)
class DissertationAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'language', 'get_categories', 'publication_date')
    list_filter = ('language', 'categories')
    search_fields = ('title', 'author', 'content')
    list_per_page = 25

    def get_categories(self, obj):
        return get_categories(obj)
    get_categories.short_description = 'Категории'

@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  
    search_fields = ('name',)
    list_per_page = 25

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')  
    list_filter = ('parent',)
    search_fields = ('name',)
    list_per_page = 25

@admin.register(DissertationCategory)
class DissertationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent') 
    list_filter = ('parent',)
    search_fields = ('name',)
    list_per_page = 25