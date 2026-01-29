"""
Main URL configuration for SMU Digital Library.
Features API versioning and clean separation of concerns.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from content.views import admin_statistics, admin_statistics_data, admin_chart

# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="SMU Digital Library API",
        default_version="v1",
        description="SMU Digital Library API - Full-text search, content management, and user interactions",
        terms_of_service="https://smu.edu.tm/terms/",
        contact=openapi.Contact(email="api@smu.edu.tm"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
)

urlpatterns = [
    # Admin interface
    path("admin/", admin.site.urls),
    # Admin statistics
    path("admin/statistics/", admin_statistics, name="admin_statistics"),
    path("admin/statistics/data/", admin_statistics_data, name="admin_statistics_data"),
    path(
        "admin/statistics/chart/<str:chart_name>.<str:fmt>",
        admin_chart,
        name="admin_chart",
    ),
    # API v1
    path("api/v1/", include("content.api.v1.urls", namespace="api_v1")),
    # API Documentation
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger",
    ),
    path(
        "api/docs/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"
    ),
    path("api/docs/schema/", schema_view.without_ui(cache_timeout=0), name="schema"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Optional django-silk profiling (development only)
if os.environ.get("DJANGO_ENABLE_SILK", "0").lower() in ("1", "true", "yes"):
    try:
        urlpatterns = [
            path("silk/", include("silk.urls", namespace="silk"))
        ] + urlpatterns
    except ImportError:
        pass

    except Exception:
        pass
