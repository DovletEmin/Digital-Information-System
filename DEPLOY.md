# Деплой на сервере - Простая инструкция

## 📦 Что нужно на сервере

- Docker
- Docker Compose
- Git (для клонирования проекта)

## 🚀 Быстрый старт

### 1. Клонировать проект

```bash
git clone https://github.com/yourusername/smu-library.git
cd smu-library
```

### 2. Создать .env файл

```bash
nano .env
```

Минимальная конфигурация:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost

# Database
POSTGRES_DB=smu
POSTGRES_USER=smu
POSTGRES_PASSWORD=strong-password-here
DATABASE_URL=postgresql://smu:strong-password-here@db:5432/smu

# Redis
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# CORS (укажите домен фронтенда)
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 3. Сгенерировать SECRET_KEY

```bash
# Используйте Python для генерации ключа
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Скопируйте результат в `SECRET_KEY` в .env файле.

### 4. Запустить проект

```bash
# Сборка и запуск всех сервисов
docker-compose up -d --build
```

Это запустит:

- PostgreSQL (база данных)
- Redis (кэш и очередь задач)
- Elasticsearch (поиск)
- Django Web App (основное приложение)
- Celery Worker (фоновые задачи)
- Celery Beat (планировщик)

### 5. Создать суперпользователя

```bash
docker-compose exec web python manage.py createsuperuser
```

Введите username, email и password.

### 6. Проверить работу

Откройте в браузере:

- API: http://your-server-ip:8000/api/v1/
- Admin: http://your-server-ip:8000/admin/
- API Docs: http://your-server-ip:8000/api/docs/swagger/

## 🔧 Полезные команды

### Управление сервисами

```bash
# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web

# Остановить все сервисы
docker-compose down

# Остановить и удалить данные
docker-compose down -v

# Перезапустить конкретный сервис
docker-compose restart web

# Проверить статус
docker-compose ps
```

### Обновление кода

```bash
# 1. Получить последние изменения
git pull origin main

# 2. Пересобрать и перезапустить
docker-compose up -d --build

# 3. Выполнить миграции (если есть)
docker-compose exec web python manage.py migrate

# 4. Собрать статику
docker-compose exec web python manage.py collectstatic --noinput
```

### Резервное копирование

```bash
# Бэкап базы данных
docker-compose exec db pg_dump -U smu smu > backup_$(date +%Y%m%d).sql

# Восстановление из бэкапа
docker-compose exec -T db psql -U smu smu < backup_20260123.sql
```

### Очистка и обслуживание

```bash
# Пересоздать индексы Elasticsearch
docker-compose exec web python manage.py search_index --rebuild

# Очистить старые логи
docker-compose exec web python manage.py clearsessions

# Удалить неиспользуемые Docker образы
docker system prune -a
```

## 🔒 Настройка безопасности

### 1. Nginx как reverse proxy (рекомендуется)

Установите Nginx на хосте:

```bash
sudo apt update
sudo apt install nginx
```

Создайте конфигурацию:

```bash
sudo nano /etc/nginx/sites-available/smu-library
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/smu-library/staticfiles/;
    }

    location /media/ {
        alias /path/to/smu-library/media/;
    }
}
```

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/smu-library /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. SSL с Let's Encrypt

```bash
# Установить certbot
sudo apt install certbot python3-certbot-nginx

# Получить SSL сертификат
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автообновление сертификата (происходит автоматически)
sudo certbot renew --dry-run
```

### 3. Firewall

```bash
# Установить UFW
sudo apt install ufw

# Разрешить необходимые порты
sudo ufw allow 22     # SSH
sudo ufw allow 80     # HTTP
sudo ufw allow 443    # HTTPS

# Включить firewall
sudo ufw enable
```

## 📊 Мониторинг

### Просмотр ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Место на диске
df -h

# Логи Docker
docker-compose logs --tail=100 -f
```

### Проверка здоровья сервисов

```bash
# Проверить статус всех контейнеров
docker-compose ps

# Health check конкретного сервиса
docker inspect --format='{{json .State.Health}}' smu_web_1
```

## 🔄 Автоматическое обновление (опционально)

Создайте скрипт для автоматического обновления:

```bash
nano ~/update-smu.sh
```

```bash
#!/bin/bash
cd /path/to/smu-library

echo "Pulling latest changes..."
git pull origin main

echo "Building and restarting services..."
docker-compose up -d --build

echo "Running migrations..."
docker-compose exec -T web python manage.py migrate --noinput

echo "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo "Done! Application updated successfully."
```

Сделайте исполняемым:

```bash
chmod +x ~/update-smu.sh
```

## 📝 Переменные окружения (.env)

### Обязательные

| Переменная        | Описание              | Пример                        |
| ----------------- | --------------------- | ----------------------------- |
| SECRET_KEY        | Django секретный ключ | `django-insecure-xyz123...`   |
| DEBUG             | Режим отладки         | `False`                       |
| ALLOWED_HOSTS     | Разрешенные хосты     | `example.com,www.example.com` |
| POSTGRES_DB       | Имя БД                | `smu`                         |
| POSTGRES_USER     | Пользователь БД       | `smu`                         |
| POSTGRES_PASSWORD | Пароль БД             | `strong_password`             |

### Опциональные

| Переменная           | Описание          | По умолчанию                |
| -------------------- | ----------------- | --------------------------- |
| DJANGO_ENV           | Окружение         | `prod`                      |
| REDIS_URL            | URL Redis         | `redis://redis:6379/1`      |
| ELASTICSEARCH_URL    | URL Elasticsearch | `http://elasticsearch:9200` |
| CORS_ALLOWED_ORIGINS | CORS домены       | `http://localhost:3000`     |

## 🆘 Решение проблем

### Приложение не запускается

```bash
# Проверить логи
docker-compose logs web

# Проверить health check
docker-compose ps
```

### База данных недоступна

```bash
# Проверить PostgreSQL
docker-compose logs db

# Перезапустить БД
docker-compose restart db
```

### Elasticsearch не работает

```bash
# Увеличить vm.max_map_count на хосте
sudo sysctl -w vm.max_map_count=262144

# Сделать постоянным
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### Недостаточно памяти

```bash
# Проверить использование
docker stats

# Очистить неиспользуемые данные
docker system prune -a --volumes
```

### Порт 8000 занят

Измените порт в docker-compose.yml:

```yaml
services:
  web:
    ports:
      - "8080:8000" # Используйте 8080 вместо 8000
```

## 📞 Поддержка

- Документация: `/docs/`
- Issues: GitHub Issues
- Email: support@smu.edu.tm

---

## Краткая памятка команд

```bash
# Запуск
docker-compose up -d --build

# Остановка
docker-compose down

# Логи
docker-compose logs -f

# Обновление
git pull && docker-compose up -d --build

# Бэкап БД
docker-compose exec db pg_dump -U smu smu > backup.sql

# Создать админа
docker-compose exec web python manage.py createsuperuser
```

✅ **Готово к production!** Один Dockerfile, один docker-compose.yml, простой деплой.
