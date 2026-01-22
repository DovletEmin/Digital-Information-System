"""
Legacy settings.py file - Deprecated

This file is kept for backward compatibility only.
New settings structure is in src/src/settings/ directory.

Please use DJANGO_ENV environment variable to switch between dev/prod:
    DJANGO_ENV=dev  - Development settings
    DJANGO_ENV=prod - Production settings

For direct import, use:
    from src.settings import *  # Uses environment-based settings
"""

# Import from new settings structure
from src.settings import *

# Display deprecation warning
import warnings

warnings.warn(
    "Direct import from settings.py is deprecated. "
    "Please use 'from src.settings import *' or set DJANGO_ENV environment variable.",
    DeprecationWarning,
    stacklevel=2,
)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
##

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-7n_(2oo+g=p!sqgyy^^-qb-l99xsg09^2@ikglgbh4kp4ovdwo"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_yasg",
    "django_filters",
    "corsheaders",
    "ckeditor",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_celery_beat",
    "content",
]

# Optional SQL profiler (django-silk). Enable by setting DJANGO_ENABLE_SILK=1 in env.
if os.environ.get("DJANGO_ENABLE_SILK", "0").lower() in ("1", "true", "yes"):
    INSTALLED_APPS += ["silk"]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# If Silk enabled, add its middleware early to capture DB calls
if os.environ.get("DJANGO_ENABLE_SILK", "0").lower() in ("1", "true", "yes"):
    MIDDLEWARE = ["silk.middleware.SilkyMiddleware"] + MIDDLEWARE


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.55.43:3000",
]

ROOT_URLCONF = "src.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "src.wsgi.application"

DATE_FORMAT = "d-m-y"
DATETIME_FORMAT = "d-m-y H:i"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "content.authentication.authentication.JWTAuthenticationNoBearerRequired",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DATETIME_FORMAT": "%d.%m.%Y",
    "DATE_FORMAT": "%d.%m.%Y",
    "PAGE_SIZE": 8,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}

# Use fast JSON renderer (orjson) for DRF if available; keep browsable API in DEBUG
default_renderers = ["rest_framework_orjson.renderers.ORJSONRenderer"]
if DEBUG:
    default_renderers.append("rest_framework.renderers.BrowsableAPIRenderer")

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = default_renderers


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "",
        }
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "persistAuthorization": True,
}


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "smu"),
        "USER": os.environ.get("POSTGRES_USER", "smu"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "topsecret"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Keep DB connections open for a short time to reuse connections across requests/workers.
# This reduces churn and helps when many workers/processes are running.
DATABASES["default"]["CONN_MAX_AGE"] = int(os.environ.get("DJANGO_CONN_MAX_AGE", 600))


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "Asia/Ashgabat"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Bold", "Italic", "Underline"],
            ["NumberedList", "BulletedList", "Blockquote"],
            ["Link", "Unlink"],
            ["RemoveFormat", "Source"],
        ],
        "width": "100%",
        "height": 300,
        "removePlugins": "uploadimage,image,flash,iframe",
    }
}

# Silence django-ckeditor W001 system check (bundled CKEditor 4 security notice)
# NOTE: this hides the warning; prefer migrating to CKEditor5 or using CKEditor4 LTS.
SILENCED_SYSTEM_CHECKS = ["ckeditor.W001"]

ELASTICSEARCH_DSL = {
    "default": {
        # Prefer explicit env var; default to localhost (host machine) where
        # Elasticsearch is published when running via docker-compose.
        "hosts": os.environ.get("ELASTICSEARCH_URL", "http://127.0.0.1:9200"),
    },
}

# Celery configuration (sane defaults for local development)
# Broker reachable from host when Redis is published by docker-compose
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
# When True, tasks run locally and synchronously (useful for local dev without broker)
CELERY_TASK_ALWAYS_EAGER = os.environ.get(
    "CELERY_TASK_ALWAYS_EAGER", "False"
).lower() in ("1", "true", "yes")

# Cache configuration: prefer Redis when `REDIS_URL` is provided, otherwise use local memory cache.
if os.environ.get("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.environ.get("REDIS_URL"),
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-smu",
        }
    }

# Optional SQL logging for debugging slow queries.
# Set environment variable `DJANGO_SQL_DEBUG=1` to enable DEBUG logging for DB.
SQL_DEBUG = os.environ.get("DJANGO_SQL_DEBUG", "0").lower() in ("1", "true", "yes")

# Ensure logging is configured regardless of cache backend selection.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG" if SQL_DEBUG else "WARNING",
            "propagate": False,
        },
    },
}
