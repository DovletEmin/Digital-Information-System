from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from content.views import (
    ArticleViewSet,
    BookViewSet,
    DissertationViewSet,
    ArticleCategoryViewSet,
    BookCategoryViewSet,
    DissertationCategoryViewSet,
    RegisterView,
    ToggleBookmarkView,
    UserBookmarksView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from content.authentication.views import LogoutView

router = routers.DefaultRouter()
router.register(r"articles", ArticleViewSet)
router.register(r"books", BookViewSet)
router.register(r"dissertations", DissertationViewSet)
router.register(r"article-categories", ArticleCategoryViewSet)
router.register(r"book-categories", BookCategoryViewSet)
router.register(r"dissertation-categories", DissertationCategoryViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="SMU API",
        default_version="v1",
        description="API для Sanly Maglumat Ulgamy",
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    # Закладки
    path(
        "bookmarks/toggle/<int:pk>/",
        ToggleBookmarkView.as_view(),
        name="toggle-bookmark",
    ),
    path(
        "bookmarks/",
        UserBookmarksView.as_view(
            authentication_classes=[JWTAuthentication],
            permission_classes=[IsAuthenticated],
        ),
        name="my-bookmarks",
    ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
