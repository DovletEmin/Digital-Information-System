from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from content.views import (
    ArticleViewSet, BookViewSet, DissertationViewSet,
    ArticleCategoryViewSet, BookCategoryViewSet, DissertationCategoryViewSet
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'books', BookViewSet)
router.register(r'dissertations', DissertationViewSet)
router.register(r'article-categories', ArticleCategoryViewSet)
router.register(r'book-categories', BookCategoryViewSet)
router.register(r'dissertation-categories', DissertationCategoryViewSet)


schema_view = get_schema_view(
    openapi.Info(
        title="Sanly Maglumat Ulgamy API",
        default_version="v1"
        description="API для получения статей, книг и диссертаций (только GET)",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)