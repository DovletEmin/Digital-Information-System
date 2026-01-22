# 🚀 Upgrade Guide: v1.0 → v2.0

This guide helps you upgrade your SMU Digital Library from version 1.0 to 2.0 with minimal downtime.

## ⚠️ CRITICAL: Backup First!

```bash
# Backup database
docker-compose exec -T db pg_dump -U smu smu > backup_before_v2.sql

# Backup .env file
cp .env .env.backup

# Backup media files (if not using volumes)
tar -czf media_backup.tar.gz src/media/
```

## 📋 Pre-Upgrade Checklist

- [ ] Current version is running and stable
- [ ] Database backup created
- [ ] `.env` backup created
- [ ] Media files backed up (if applicable)
- [ ] Maintenance window scheduled
- [ ] Team notified of upgrade

## 🔧 Upgrade Steps

### 1. Pull Latest Code

```bash
git fetch origin
git checkout v2.0.0  # or main/master for latest
```

### 2. Update .env File

Add new required variables:

```bash
# Add these to your .env file
DJANGO_ENV=dev  # or 'prod' for production

# Generate a new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Add it to .env: SECRET_KEY=<generated-key>

# Optional (already have defaults)
DJANGO_CONN_MAX_AGE=600
```

### 3. Update Frontend API URLs

**IMPORTANT**: API endpoints have moved from `/api/` to `/api/v1/`

#### Before (v1.0):

```javascript
const API_BASE = "http://localhost:8000/api/";
```

#### After (v2.0):

```javascript
const API_BASE = "http://localhost:8000/api/v1/";
```

Update all API calls in your frontend:

- `/api/articles/` → `/api/v1/articles/`
- `/api/books/` → `/api/v1/books/`
- `/auth/login/` → `/api/v1/auth/login/`
- `/search/` → `/api/v1/search/`
- etc.

### 4. Rebuild Docker Images

```bash
# Stop current services
docker-compose down

# Rebuild with new code
docker-compose build --no-cache

# Start services
docker-compose up -d
```

### 5. Run Migrations

```bash
# Migrations are automatic on startup, but you can run manually:
docker-compose exec web python manage.py migrate

# Verify migrations
docker-compose exec web python manage.py showmigrations
```

### 6. Collect Static Files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 7. Verify Services

```bash
# Check all services are running
docker-compose ps

# Check web service logs
docker-compose logs web

# Test health check
curl http://localhost:8000/api/v1/
```

### 8. Test Critical Endpoints

```bash
# Test API root
curl http://localhost:8000/api/v1/

# Test articles endpoint
curl http://localhost:8000/api/v1/articles/

# Test search
curl "http://localhost:8000/api/v1/search/?q=test"

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

## 🔄 Rollback Procedure

If something goes wrong:

```bash
# 1. Stop services
docker-compose down

# 2. Checkout previous version
git checkout v1.0.0

# 3. Restore .env
cp .env.backup .env

# 4. Restore database
cat backup_before_v2.sql | docker-compose exec -T db psql -U smu smu

# 5. Rebuild and start
docker-compose build
docker-compose up -d
```

## 🆕 New Features in v2.0

### API Changes

- ✅ API versioning: `/api/v1/`
- ✅ Improved error responses (standardized format)
- ✅ Rate limiting on all endpoints
- ✅ Better search error handling

### Security Improvements

- ✅ SECRET_KEY from environment
- ✅ DEBUG configurable
- ✅ Strong password validation
- ✅ Email validation on registration
- ✅ Production security headers

### Developer Experience

- ✅ Split settings (base/dev/prod)
- ✅ Split requirements
- ✅ Comprehensive README
- ✅ Makefile for convenience
- ✅ Better logging

### Infrastructure

- ✅ Health checks for all services
- ✅ Proper service dependencies
- ✅ Separate static/media volumes
- ✅ Improved Docker setup

## 🐛 Known Issues & Solutions

### Issue: "Settings module not found"

**Solution**: Check DJANGO_ENV environment variable

```bash
# Should be 'dev' or 'prod'
echo $DJANGO_ENV
```

### Issue: "Secret key is required"

**Solution**: Generate and set SECRET_KEY in .env

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Issue: API 404 errors

**Solution**: Update frontend URLs from `/api/` to `/api/v1/`

### Issue: Rate limiting too strict

**Solution**: Adjust in settings/base.py or settings/prod.py:

```python
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": "200/hour",  # Increase from 100
    "user": "2000/hour",  # Increase from 1000
}
```

## 📊 Performance Expectations

After upgrade, you should see:

- ✅ Faster API responses (better caching)
- ✅ Lower database load (query optimization)
- ✅ Better error recovery (proper error handling)
- ✅ More detailed logs (structured logging)

## 🎓 Training Resources

### For Developers

- [README.md](README.md) - Complete documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [API Documentation](http://localhost:8000/api/docs/swagger/)

### For Users

- API endpoints remain functionally the same
- Only URL paths have changed (`/api/` → `/api/v1/`)
- All features work as before

## ✅ Post-Upgrade Checklist

- [ ] All services running (`docker-compose ps`)
- [ ] Health checks passing
- [ ] Frontend connects successfully
- [ ] Authentication works
- [ ] Search functionality works
- [ ] User bookmarks accessible
- [ ] Content rating works
- [ ] Admin panel accessible
- [ ] Celery tasks processing
- [ ] Elasticsearch indexing working

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Check this guide's Known Issues section
3. Review README.md troubleshooting
4. Open an issue on GitHub
5. Contact: support@smu.edu.tm

## 🎉 Success!

If all checklist items are ✅, your upgrade is complete!

Welcome to v2.0 - enjoy the improved performance, security, and developer experience!

---

**Upgrade completed on**: [Add date]  
**Upgraded by**: [Your name]  
**Downtime**: [Actual downtime]  
**Issues encountered**: [None / List issues]
