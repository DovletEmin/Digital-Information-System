# 🚀 Quick Start Cheat Sheet

## Initial Setup (First Time Only)

```bash
# 1. Clone and enter directory
git clone <repo-url>
cd smu-library

# 2. Copy and configure .env
cp .env.example .env

# 3. Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Add to .env: SECRET_KEY=<generated-key>

# 4. Build and start
make build
make up

# 5. Create superuser
make createsuperuser

# 6. Access
# API: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/
# Docs: http://localhost:8000/api/docs/swagger/
```

## Daily Development Commands

```bash
# Start services
make up

# Stop services
make down

# View logs
make logs              # All services
make logs-web          # Web only
make logs-celery       # Celery only

# Django shell
make shell

# Container bash
make bash

# Run migrations
make migrate

# Create migrations
make makemigrations

# Collect static files
make collectstatic

# Run tests
make test
make test-cov          # With coverage

# Code quality
make lint              # Check code
make format            # Format code
```

## Common Tasks

### Create New Model

```python
# 1. Edit models.py
class MyModel(models.Model):
    name = models.CharField(max_length=100)

# 2. Create migration
make makemigrations

# 3. Apply migration
make migrate
```

### Add New API Endpoint

```python
# 1. Create view in src/content/api/v1/views.py
class MyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer

# 2. Register in src/content/api/v1/urls.py
router.register(r'my-models', views.MyViewSet, basename='mymodel')

# 3. Test
curl http://localhost:8000/api/v1/my-models/
```

### Debug Issues

```bash
# Check service status
docker-compose ps

# View recent logs
make logs

# Check migrations
make shell
>>> from django.db import connection
>>> connection.introspection.table_names()

# Test Elasticsearch
curl http://localhost:9200/_cluster/health

# Test Redis
docker-compose exec redis redis-cli ping
```

## Environment Variables

```bash
# Core
DJANGO_ENV=dev              # dev or prod
SECRET_KEY=<your-key>       # Required
DEBUG=True                  # False in prod

# Database
POSTGRES_DB=smu
POSTGRES_USER=smu
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=db

# Services
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
ELASTICSEARCH_URL=http://elasticsearch:9200

# Optional
DJANGO_ENABLE_SILK=1        # Enable SQL profiling
DJANGO_SQL_DEBUG=1          # Enable SQL logging
```

## API Quick Reference

```bash
# Base URL
API_BASE="http://localhost:8000/api/v1"

# Auth
POST $API_BASE/auth/register/
POST $API_BASE/auth/login/
POST $API_BASE/auth/refresh/
POST $API_BASE/auth/logout/

# Content
GET  $API_BASE/articles/
GET  $API_BASE/articles/123/
GET  $API_BASE/books/
GET  $API_BASE/dissertations/

# Search
GET  $API_BASE/search/?q=query

# User
POST $API_BASE/bookmarks/toggle/123/
GET  $API_BASE/bookmarks/
POST $API_BASE/rate/
POST $API_BASE/views/article/123/
```

## Wheelhouse (Offline Builds)

```bash
# Download dev wheels
make download-wheels

# Download all wheels (base + dev + prod)
make download-wheels-all

# Download specific environment
python scripts/download_wheels.py --env base
python scripts/download_wheels.py --env prod

# Check wheelhouse
ls wheelhouse/*.whl | wc -l  # Count wheels
du -sh wheelhouse/           # Check size

# Why use wheelhouse?
# - Faster Docker builds (2-3x)
# - Offline builds (no internet needed)
# - Consistent dependencies
# - CI/CD optimization
```

## Testing

```bash
# Run all tests
make test

# Run specific test file
docker-compose exec web pytest src/content/tests/test_api.py

# Run with coverage
make test-cov

# View coverage report
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

## Database

```bash
# Backup
make backup-db

# Restore
make restore-db

# Reset database
make down
docker volume rm smu_pgdata
make up
make migrate
make createsuperuser

# Access PostgreSQL
docker-compose exec db psql -U smu smu
```

## Troubleshooting

### Port Already in Use

```bash
# Find process
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Kill process or change port in docker-compose.yml
```

### Permission Denied

```bash
# Linux/Mac: Fix permissions
sudo chown -R $USER:$USER .

# Windows: Run as Administrator or check Docker settings
```

### Services Won't Start

```bash
# Check logs
make logs

# Rebuild from scratch
make clean
make build
make up
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps db

# Check credentials in .env
grep POSTGRES .env

# Restart database
docker-compose restart db
```

### Elasticsearch Not Working

```bash
# Check Elasticsearch status
curl http://localhost:9200

# Check logs
docker-compose logs elasticsearch

# Restart Elasticsearch
docker-compose restart elasticsearch

# Rebuild search index
make rebuild-search
```

## Git Workflow

```bash
# Update from main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature

# Make changes, commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/my-feature

# After merge, update main
git checkout main
git pull origin main
git branch -d feature/my-feature
```

## Performance Profiling

```bash
# Enable SQL profiling (django-silk)
export DJANGO_ENABLE_SILK=1
make restart

# Access profiling UI
open http://localhost:8000/silk/

# Disable when done
unset DJANGO_ENABLE_SILK
make restart
```

## Production Deployment

```bash
# 1. Set production environment
export DJANGO_ENV=prod

# 2. Update .env for production
DJANGO_ENV=prod
SECRET_KEY=<strong-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# 3. Build production image
docker build --build-arg ENV=prod -t smu-library:prod .

# 4. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl https://yourdomain.com/api/v1/
```

## Useful URLs

- 📚 API Docs: http://localhost:8000/api/docs/swagger/
- 🔧 Admin: http://localhost:8000/admin/
- 🐌 SQL Profiler: http://localhost:8000/silk/ (when enabled)
- 🔍 Elasticsearch: http://localhost:9200
- 📊 Redis: redis://localhost:6379

## Code Snippets

### Create Django Command

```python
# src/content/management/commands/mycommand.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'My custom command'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Success!'))
```

### Add Custom Middleware

```python
# src/content/middleware.py
class MyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before view
        response = self.get_response(request)
        # After view
        return response

# Add to MIDDLEWARE in settings
```

### Create Custom Throttle

```python
# src/content/utils/throttles.py
from rest_framework.throttling import UserRateThrottle

class MyThrottle(UserRateThrottle):
    scope = 'my_scope'
    rate = '10/minute'

# Add to view
class MyView(APIView):
    throttle_classes = [MyThrottle]
```

---

**💡 Pro Tips:**

1. Always work in feature branches
2. Write tests for new features
3. Run `make lint` before committing
4. Check logs when debugging
5. Use `.only()` for query optimization
6. Cache expensive operations
7. Document your code
8. Keep .env file secure (never commit!)

---

**Need more help?**

- 📖 See [README.md](README.md) for full documentation
- 🔍 Check [API_EXAMPLES.md](API_EXAMPLES.md) for API usage
- 🐛 See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
