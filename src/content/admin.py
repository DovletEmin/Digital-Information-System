# content/admin.py — САМАЯ ЛУЧШАЯ АДМИНКА В ТУРКМЕНИСТАНЕ

from django.contrib import admin
from django.urls import reverse, path
from .models import (
    Article,
    Book,
    Dissertation,
    ArticleCategory,
    BookCategory,
    DissertationCategory,
)


# === КАСТОМНАЯ АДМИНКА С КНОПКОЙ "СТАТИСТИКА" ===
class SMUAdminSite(admin.AdminSite):
    site_header = "SMU Sanly Kitaphanasy — Administrasiýa"
    site_title = "SMU Admin"
    index_title = "Baş sahypa"

    def get_urls(self):
        urls = super().get_urls()
        from content.views import admin_statistics

        custom_urls = [
            path(
                "statistics/",
                self.admin_view(admin_statistics),
                name="admin_statistics",
            ),
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["statistics_url"] = reverse("admin:admin_statistics")
        return super().index(request, extra_context)


# Создаём и активируем нашу админку
admin.site = SMUAdminSite(name="smuadmin")


# === ФУНКЦИЯ ДЛЯ КАТЕГОРИЙ ===
def get_categories(obj):
    return (
        ", ".join([c.name for c in obj.categories.all()])
        if obj.categories.exists()
        else "—"
    )


get_categories.short_description = "Kategoriýalar"


# === РЕГИСТРАЦИЯ МОДЕЛЕЙ В НАШЕЙ АДМИНКЕ ===
@admin.register(Article, site=admin.site)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "language",
        get_categories,
        "publication_date",
        "views",
        "average_rating",
    )
    list_filter = ("language", "type", "categories", "publication_date")
    search_fields = ("title", "author", "content", "source_name")
    readonly_fields = ("views", "average_rating", "rating_count")
    list_per_page = 25


@admin.register(Book, site=admin.site)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "language",
        get_categories,
        "views",
        "average_rating",
    )
    list_filter = ("language", "categories")
    search_fields = ("title", "author", "content")
    readonly_fields = ("views", "average_rating", "rating_count")
    list_per_page = 25


@admin.register(Dissertation, site=admin.site)
class DissertationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "language",
        get_categories,
        "publication_date",
        "views",
        "average_rating",
    )
    list_filter = ("language", "categories", "publication_date")
    search_fields = ("title", "author", "content")
    readonly_fields = ("views", "average_rating", "rating_count")
    list_per_page = 25


@admin.register(ArticleCategory, site=admin.site)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(BookCategory, site=admin.site)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    list_filter = ("parent",)
    search_fields = ("name",)


@admin.register(DissertationCategory, site=admin.site)
class DissertationCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    list_filter = ("parent",)
    search_fields = ("name",)


# === ДОБАВЛЯЕМ КНОПКУ "СТАТИСТИКА" НА ГЛАВНУЮ СТРАНИЦУ ===
def get_app_list(self, request, extra_context=None):
    app_list = super(SMUAdminSite, self).get_app_list(request)
    app_list += [
        {
            "name": "Statistika we analitika",
            "app_label": "content",
            "models": [
                {
                    "name": "Umumy statistika",
                    "object_name": "statistics",
                    "admin_url": reverse("admin:admin_statistics"),
                    "view_only": True,
                }
            ],
        }
    ]
    return app_list


# Привязываем метод к нашей админке
SMUAdminSite.get_app_list = get_app_list
