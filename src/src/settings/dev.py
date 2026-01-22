"""
Development settings for SMU Digital Library project.
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-dev-key-change-in-production"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

# Development-specific apps
DEV_APPS = []

# Optional SQL profiler (django-silk) for development
if os.environ.get("DJANGO_ENABLE_SILK", "0").lower() in ("1", "true", "yes"):
    DEV_APPS.append("silk")
    MIDDLEWARE = ["silk.middleware.SilkyMiddleware"] + MIDDLEWARE

INSTALLED_APPS += DEV_APPS

# Enable SQL debug logging if requested
SQL_DEBUG = os.environ.get("DJANGO_SQL_DEBUG", "0").lower() in ("1", "true", "yes")
if SQL_DEBUG:
    LOGGING["loggers"]["django.db.backends"]["level"] = "DEBUG"

# Development cache settings (short TTL for testing)
CACHES["default"]["TIMEOUT"] = 60

# Email backend for development (console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
