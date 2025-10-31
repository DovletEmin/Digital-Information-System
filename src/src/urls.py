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
router.register(r'Makalalar', ArticleViewSet)
router.register(r'Kitaplar', BookViewSet)
router.register(r'Dissertasiýalar', DissertationViewSet)
router.register(r'Makalala-Kategoriýalar', ArticleCategoryViewSet)
router.register(r'Kitap-Kategoriýalar', BookCategoryViewSet)
router.register(r'Dissertasiýa-Kategoriýalar', DissertationCategoryViewSet)


schema_view = get_schema_view(
    openapi.Info(
        title="Sanly Maglumat Ulgamy API",
        default_version="v1",
        description="API для получения статей, книг и диссертаций (только GET)",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)