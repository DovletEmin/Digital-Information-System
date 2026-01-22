# CHANGELOG

All notable changes to SMU Digital Library project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-20

### 🎉 Major Refactoring - Professional Edition

#### Added

- **API Versioning**: Introduced `/api/v1/` structure for future compatibility
- **Environment-based Settings**: Split settings into `base.py`, `dev.py`, `prod.py`
- **Requirements Split**: Separated dependencies for different environments
- **Professional Mixins**:
  - `BookmarkAnnotateMixin` for DRY bookmark logic
  - `CachedRetrieveMixin` for efficient caching
  - `ContentListOptimizationMixin` for query optimization
- **Custom Throttling**: Added `SearchRateThrottle`, `AuthRateThrottle`
- **Exception Handler**: Standardized API error responses
- **Utilities Package**: Organized helpers, throttles, and exception handlers
- **Comprehensive README**: Full documentation with architecture diagrams
- **Makefile**: Convenient command-line shortcuts
- **Health Checks**: Added health checks for all Docker services
- **Logging**: File and console logging with rotation

#### Security

- ✅ SECRET_KEY moved to environment variables
- ✅ DEBUG made configurable
- ✅ ALLOWED_HOSTS from environment
- ✅ Rate limiting on all endpoints
- ✅ Strong password validation
- ✅ Email validation on registration
- ✅ Production security headers (HSTS, X-Frame-Options, etc.)
- ✅ CORS properly configured

#### Changed

- **URL Structure**: Migrated from `/api/` to `/api/v1/`
- **Views**: Refactored using composition with mixins
- **Search**: Improved error handling and Elasticsearch client management
- **Docker Compose**:
  - Added proper healthchecks
  - Removed migrations from Celery workers
  - Added service dependencies
  - Created separate volumes for static/media
- **Serializers**: Enhanced UserSerializer with validation
- **Settings**: Organized into environment-specific modules

#### Fixed

- 🐛 Fixed `get_serializer_class()` indentation bug in ViewSets
- 🐛 API responses now in English (not Russian)
- 🐛 Elasticsearch connection properly managed as singleton
- 🐛 Cache versioning for proper invalidation

#### Removed

- ❌ Hardcoded SECRET_KEY from settings
- ❌ DEBUG always True
- ❌ migrations/ from .gitignore
- ❌ SQL debug in production
- ❌ Unnecessary code duplication in ViewSets

### Architecture Improvements

#### Design Patterns Applied

1. **Mixin Pattern**: Reusable functionality across ViewSets
2. **Singleton Pattern**: Elasticsearch client management
3. **Template Method Pattern**: Content list optimization
4. **Strategy Pattern**: Different throttling strategies
5. **Decorator Pattern**: Cached retrieval wrapper

#### Code Quality

- Removed code duplication (DRY principle)
- Improved separation of concerns
- Better error handling
- Type hints in critical sections
- Comprehensive docstrings

### Migration Guide

#### For Developers

1. Update `.env` file with new variables:

```bash
DJANGO_ENV=dev
SECRET_KEY=<generate-new-key>
```

2. Update API URLs in frontend:

```javascript
// Old
fetch("/api/articles/");

// New
fetch("/api/v1/articles/");
```

3. Install new requirements:

```bash
pip install -r requirements/dev.txt
```

#### For Production

1. Set environment variables:

```bash
DJANGO_ENV=prod
SECRET_KEY=<strong-secret-key>
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

2. Build with production settings:

```bash
docker build --build-arg ENV=prod -t smu-library:prod .
```

## [1.0.0] - 2024-XX-XX

### Initial Release

- Django REST Framework API
- Elasticsearch full-text search
- Celery async tasks
- JWT authentication
- Content management (Articles, Books, Dissertations)
- User bookmarks and ratings
- Basic Docker setup
