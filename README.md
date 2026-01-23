# SMU Digital Library 📚

Professional digital library system for Sarynyýazov Myrat University with full-text search, content management, and user interactions.

## 🎯 Features

- **Full-Text Search**: Powered by Elasticsearch with fuzzy matching and highlighting
- **Content Management**: Articles, Books, and Dissertations with rich metadata
- **User System**: Registration, authentication with JWT, bookmarks, and ratings
- **RESTful API**: Clean, versioned API with comprehensive documentation
- **Async Processing**: Celery workers for search indexing and background tasks
- **Multilingual**: Support for Turkmen, Russian, and English content
- **Performance**: Redis caching, optimized queries, rate limiting
- **Professional**: API versioning, proper error handling, logging

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│    Nginx     │────▶│  Django App │
│ (Frontend)  │     │ (Reverse     │     │  (Gunicorn) │
└─────────────┘     │   Proxy)     │     └─────────────┘
                    └──────────────┘            │
                                                │
              ┌─────────────────────────────────┴──────────┐
              │                                            │
       ┌──────▼──────┐     ┌──────────────┐     ┌────────▼────────┐
       │  PostgreSQL │     │ Elasticsearch│     │     Redis       │
       │  (Main DB)  │     │   (Search)   │     │ (Cache/Broker)  │
       └─────────────┘     └──────────────┘     └─────────────────┘
                                                          │
                                               ┌──────────▼────────┐
                                               │  Celery Workers   │
                                               │  & Beat Scheduler │
                                               └───────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/smu-library.git
cd smu-library
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Generate a strong SECRET_KEY**

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

4. **Build and start services**

```bash
docker-compose up -d --build
```

5. **Create superuser**

```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Access the application**

- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/swagger/

### Деплой на сервере

Полная инструкция по деплою на production сервере: [DEPLOY.md](DEPLOY.md)

## 📚 API Documentation

### Base URL

```
Development: http://localhost:8000/api/v1/
Production: https://api.smu.edu.tm/api/v1/
```

### Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

### Key Endpoints

#### Authentication

- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login and get tokens
- `POST /api/v1/auth/refresh/` - Refresh access token
- `POST /api/v1/auth/logout/` - Logout

#### Content

- `GET /api/v1/articles/` - List articles
- `GET /api/v1/articles/{id}/` - Get article details
- `GET /api/v1/books/` - List books
- `GET /api/v1/books/{id}/` - Get book details
- `GET /api/v1/dissertations/` - List dissertations
- `GET /api/v1/dissertations/{id}/` - Get dissertation details

#### Search

- `GET /api/v1/search/?q=<query>` - Full-text search across all content

#### User Interactions

- `POST /api/v1/bookmarks/toggle/{id}/` - Add/remove bookmark
- `GET /api/v1/bookmarks/` - Get user bookmarks
- `POST /api/v1/rate/` - Rate content (1-5 stars)
- `POST /api/v1/views/{type}/{id}/` - Register content view

### Filtering & Pagination

Most list endpoints support filtering:

```bash
# Filter by language
GET /api/v1/articles/?language=tm

# Filter by category
GET /api/v1/books/?categories=5

# Date range
GET /api/v1/articles/?publication_date__gte=2024-01-01&publication_date__lte=2024-12-31

# Pagination
GET /api/v1/articles/?page=2
```

## 🛠️ Development

### Project Structure

```
smu-library/
├── src/
│   ├── content/                    # Main app
│   │   ├── api/
│   │   │   └── v1/                 # API v1
│   │   │       ├── views.py        # API views
│   │   │       ├── urls.py         # API URLs
│   │   │       └── search.py       # Search logic
│   │   ├── authentication/         # Auth logic
│   │   ├── management/             # Django commands
│   │   ├── utils/                  # Utilities
│   │   │   ├── mixins.py           # Reusable mixins
│   │   │   ├── throttles.py        # Rate limiting
│   │   │   ├── exception_handlers.py
│   │   │   └── helpers.py
│   │   ├── models.py               # Data models
│   │   ├── serializers.py          # DRF serializers
│   │   ├── tasks.py                # Celery tasks
│   │   └── signals.py              # Django signals
│   └── src/                        # Project settings
│       ├── settings/
│       │   ├── base.py             # Base settings
│       │   ├── dev.py              # Development
│       │   └── prod.py             # Production
│       ├── urls.py
│       └── wsgi.py/asgi.py
├── requirements.txt                # All dependencies
├── docker-compose.yml
├── Dockerfile
└── README.md
```

### Local Development Setup

1. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up database**

```bash
python src/manage.py migrate
python src/manage.py createsuperuser
```

4. **Run development server**

```bash
cd src
python manage.py runserver
```

5. **Run Celery worker (separate terminal)**

```bash
cd src
celery -A src worker --loglevel=info
```

6. **Run Celery beat (separate terminal)**

```bash
cd src
celery -A src beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Code Quality

```bash
# Run ruff linter
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
autopep8 --in-place --recursive .
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=content --cov-report=html

# Run specific test file
pytest src/content/tests.py
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable            | Description            | Default                     |
| ------------------- | ---------------------- | --------------------------- |
| `DJANGO_ENV`        | Environment (dev/prod) | `dev`                       |
| `SECRET_KEY`        | Django secret key      | Required                    |
| `DEBUG`             | Debug mode             | `False`                     |
| `ALLOWED_HOSTS`     | Comma-separated hosts  | Required in prod            |
| `POSTGRES_DB`       | Database name          | `smu`                       |
| `POSTGRES_USER`     | Database user          | `smu`                       |
| `POSTGRES_PASSWORD` | Database password      | Required                    |
| `REDIS_URL`         | Redis connection URL   | `redis://redis:6379/1`      |
| `ELASTICSEARCH_URL` | Elasticsearch URL      | `http://elasticsearch:9200` |

### Settings Files

The project uses environment-based settings:

- **base.py**: Common settings for all environments
- **dev.py**: Development-specific settings (debug tools, lenient security)
- **prod.py**: Production settings (strict security, optimizations)

Set `DJANGO_ENV=prod` for production mode.

## 🚀 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Set `DJANGO_ENV=prod`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure email backend
- [ ] Set up backup strategy for PostgreSQL
- [ ] Configure monitoring (Sentry recommended)
- [ ] Set up log rotation
- [ ] Review and adjust throttle rates
- [ ] Configure CORS origins

### Docker Production Build

```bash
# Build production image
docker build --build-arg ENV=prod -t smu-library:latest .

# Run with production settings
docker-compose -f docker-compose.prod.yml up -d
```

### Database Backups

```bash
# Backup
docker-compose exec db pg_dump -U smu smu > backup_$(date +%Y%m%d).sql

# Restore
cat backup.sql | docker-compose exec -T db psql -U smu smu
```

## 📊 Monitoring

### Health Checks

- Web: `GET /api/v1/` (returns 200 if healthy)
- Database: Automatic healthcheck in docker-compose
- Elasticsearch: Automatic healthcheck in docker-compose
- Redis: Automatic healthcheck in docker-compose

### Logging

Logs are stored in `/app/logs/` directory:

- `django.log`: Application logs
- Console output for real-time monitoring

### Performance Monitoring

Enable django-silk for SQL profiling:

```bash
DJANGO_ENABLE_SILK=1
```

Access at: http://localhost:8000/silk/

## 🔒 Security

### Implemented Security Measures

- ✅ JWT authentication with token blacklisting
- ✅ Rate limiting on all endpoints
- ✅ CORS configuration
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection headers
- ✅ HTTPS enforcement in production
- ✅ Secure password hashing (PBKDF2)
- ✅ Password strength validation
- ✅ Session security
- ✅ CSRF protection

### Security Best Practices

1. Never commit `.env` file
2. Use strong, unique SECRET_KEY
3. Keep dependencies updated
4. Review logs regularly
5. Use HTTPS in production
6. Implement API rate limiting
7. Regular security audits

## 📝 API Rate Limits

| User Type      | Rate Limit                           |
| -------------- | ------------------------------------ |
| Anonymous      | 100/hour (general), 30/min (search)  |
| Authenticated  | 1000/hour (general), 30/min (search) |
| Auth endpoints | 5/minute                             |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for functions/classes
- Keep functions small and focused
- Use meaningful variable names

## 📄 License

Copyright © 2026 Sarynyýazov Myrat University. All rights reserved.

## 👥 Authors

- Development Team - SMU IT Department

## 🆘 Support

For support, email support@smu.edu.tm or open an issue in the repository.

## 📈 Roadmap

- [ ] GraphQL API endpoint
- [ ] WebSocket support for real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Content recommendation engine
- [ ] Mobile app support
- [ ] Multi-tenancy support
- [ ] Advanced search filters
- [ ] PDF generation for content

---

**Made with ❤️ for SMU Digital Library**
