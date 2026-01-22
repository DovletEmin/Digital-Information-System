"""
API v1 URL configuration.
"""

from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from content.api.v1 import views
from content.authentication.views import LogoutView
from content.api.v1.search import ContentSearchView
from content.views import admin_statistics, admin_statistics_data, admin_chart

# Create router for viewsets
router = routers.DefaultRouter()
router.register(r"articles", views.ArticleViewSet, basename="article")
router.register(r"books", views.BookViewSet, basename="book")
router.register(r"dissertations", views.DissertationViewSet, basename="dissertation")
router.register(
    r"article-categories", views.ArticleCategoryViewSet, basename="article-category"
)
router.register(r"book-categories", views.BookCategoryViewSet, basename="book-category")
router.register(
    r"dissertation-categories",
    views.DissertationCategoryViewSet,
    basename="dissertation-category",
)

app_name = "api_v1"

urlpatterns = [
    # Viewsets
    path("", include(router.urls)),
    # Authentication
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    # Bookmarks
    path(
        "bookmarks/toggle/<int:pk>/",
        views.ToggleBookmarkView.as_view(),
        name="toggle-bookmark",
    ),
    path("bookmarks/", views.UserBookmarksView.as_view(), name="user-bookmarks"),
    # Content interactions
    path("rate/", views.RateContentView.as_view(), name="rate-content"),
    path(
        "views/<str:content_type>/<int:pk>/",
        views.RegisterViewHit.as_view(),
        name="register-view",
    ),
    # Search
    path("search/", ContentSearchView.as_view(), name="content-search"),
]
