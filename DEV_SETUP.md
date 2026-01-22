# Development Environment Setup

Инструкции по настройке и запуску окружения разработки для SMU Digital Library.

## Требования

- Docker Desktop (для Windows)
- Docker Compose
- Git

## Быстрый старт

### 1. Создайте файл .env

Скопируйте пример конфигурации:

```bash
cp .env.example .env
```

Или создайте `.env` с минимальными настройками:

```env
# Database
POSTGRES_DB=smu
POSTGRES_USER=smu
POSTGRES_PASSWORD=smu
DATABASE_URL=postgresql://smu:smu@db:5432/smu

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Redis & Celery
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# Environment
DJANGO_ENV=development
```

### 2. Соберите и запустите контейнеры

```bash
# Сборка образов
docker-compose -f docker-compose.dev.yml build

# Запуск всех сервисов
docker-compose -f docker-compose.dev.yml up
```

Или в фоновом режиме:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Доступ к приложению

После запуска:

- **API**: http://localhost:8000/api/v1/
- **Admin**: http://localhost:8000/admin/
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Elasticsearch**: http://localhost:9200/

## Полезные команды

### Управление контейнерами

```bash
# Остановить все сервисы
docker-compose -f docker-compose.dev.yml down

# Остановить и удалить volumes
docker-compose -f docker-compose.dev.yml down -v

# Перезапустить конкретный сервис
docker-compose -f docker-compose.dev.yml restart web

# Просмотр логов
docker-compose -f docker-compose.dev.yml logs -f

# Логи конкретного сервиса
docker-compose -f docker-compose.dev.yml logs -f web
```

### Работа с Django

```bash
# Создать суперпользователя
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Выполнить миграции
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

# Собрать статику
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput

# Запустить shell
docker-compose -f docker-compose.dev.yml exec web python manage.py shell

# Создать миграции
docker-compose -f docker-compose.dev.yml exec web python manage.py makemigrations

# Загрузить тестовые данные
docker-compose -f docker-compose.dev.yml exec web python manage.py loaddata fixtures/initial_data.json
```

### Работа с Elasticsearch

```bash
# Переиндексация поиска
docker-compose -f docker-compose.dev.yml exec web python manage.py search_index --rebuild

# Обновить индексы
docker-compose -f docker-compose.dev.yml exec web python manage.py search_index --update
```

### Работа с тестами

```bash
# Запустить все тесты
docker-compose -f docker-compose.dev.yml exec web pytest

# Тесты с покрытием
docker-compose -f docker-compose.dev.yml exec web pytest --cov=content --cov-report=html

# Запустить конкретный тест
docker-compose -f docker-compose.dev.yml exec web pytest content/tests/test_models.py
```

### Отладка

```bash
# Войти в контейнер web
docker-compose -f docker-compose.dev.yml exec web bash

# Войти как root (если нужны права администратора)
docker-compose -f docker-compose.dev.yml exec -u root web bash

# Просмотр процессов в контейнере
docker-compose -f docker-compose.dev.yml exec web ps aux

# Мониторинг ресурсов
docker stats
```

### Работа с базой данных

```bash
# Подключиться к PostgreSQL
docker-compose -f docker-compose.dev.yml exec db psql -U smu -d smu

# Создать дамп базы
docker-compose -f docker-compose.dev.yml exec db pg_dump -U smu smu > backup.sql

# Восстановить дамп
docker-compose -f docker-compose.dev.yml exec -T db psql -U smu -d smu < backup.sql

# Сброс базы данных
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d db
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

## Особенности dev окружения

### Hot Reload

Код автоматически монтируется в контейнер через volumes. Изменения в коде сразу применяются без пересборки образа.

### Django Debug Toolbar

Доступен по умолчанию в dev режиме для профилирования запросов.

### Django Silk

Профилирование и мониторинг производительности доступны по адресу:
http://localhost:8000/silk/

### Порты

Все сервисы доступны напрямую для удобства разработки:

- PostgreSQL: 5432
- Redis: 6379
- Elasticsearch: 9200
- Django: 8000

### Логирование

Уровень логирования установлен на DEBUG для всех компонентов.

### Память

Ограничения по памяти для Elasticsearch снижены до 512MB для экономии ресурсов.

## Решение проблем

### Контейнеры не запускаются

```bash
# Проверить логи
docker-compose -f docker-compose.dev.yml logs

# Пересобрать образы
docker-compose -f docker-compose.dev.yml build --no-cache

# Очистить всё и начать заново
docker-compose -f docker-compose.dev.yml down -v
docker system prune -a
```

### Проблемы с миграциями

```bash
# Сбросить миграции (ВНИМАНИЕ: удалит данные)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d db
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### Elasticsearch не запускается

Увеличьте лимит виртуальной памяти:

**Windows (WSL2):**

```bash
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144
```

### Порты заняты

Если порты уже используются, измените их в docker-compose.dev.yml:

```yaml
ports:
  - "8001:8000" # Изменить 8000 на 8001
```

## Производительность

### Ограничение логов

```bash
# Очистить старые логи
docker-compose -f docker-compose.dev.yml logs --tail=100
```

### Мониторинг ресурсов

```bash
# Статистика контейнеров
docker stats

# Использование дискового пространства
docker system df
```

## Переход на production

Для production используйте:

```bash
docker-compose up -d
```

См. [README.md](README.md) для инструкций по production.
