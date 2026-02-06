# Отключение Rate Limiting и Throttling

## Выполненные изменения

✅ **Отключен throttling в Django REST Framework**

- Файл: `src/src/settings/base.py`
- Добавлено: `"DEFAULT_THROTTLE_CLASSES": []` и `"DEFAULT_THROTTLE_RATES": {}`

✅ **Отключен throttling для search endpoint**

- Файл: `src/content/api/v1/search.py`
- Добавлено: `throttle_classes = []` в `ContentSearchView`

## Действия на сервере

### 1. Обновить код на сервере

```bash
cd ~/Digital-Information-System
git pull

# ВАЖНО: Очистить Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
```

### 2. Очистить Redis кэш (важно!)

```bash
# Очистить все данные throttling в Redis
docker-compose exec redis redis-cli FLUSHDB

# Или только ключи throttle
docker-compose exec redis redis-cli --scan --pattern "throttle*" | while read key; do
    docker-compose exec redis redis-cli DEL "$key"
done
```

### 3. Пересобрать и перезапустить контейнеры

```bash
# Остановить
docker-compose down

# ВАЖНО: Пересобрать с --no-cache для обновления кода
docker-compose build --no-cache web

# Запустить
docker-compose up -d

# Подождать пока контейнер полностью запустится
sleep 10

# Проверить логи (должны быть намного чище без Silk)
docker-compose logs -f web
```

**Примечание:** Если видите много DEBUG логов от django-silk (SQL queries), это нормально в dev режиме, но в production Silk автоматически отключается.

### 4. Проверить работу

```bash
# Тест search endpoint
curl -X GET "http://192.168.55.152:8000/api/v1/search/" \
  -H "accept: application/json"

# Должен вернуться результат без ошибки 429
```

### Проверка 1: Убедитесь что изменения применились

```bash
# Проверить что throttle_classes = [] в search.py
docker-compose exec web cat /app/src/content/api/v1/search.py | grep -A 2 "class ContentSearchView"

# Должно показать:
# class ContentSearchView(APIView):
#     """..."""
#     throttle_classes = []  # Explicitly disable throttling for search

# Проверить настройки Django
docker-compose exec web python manage.py shell -c "
from django.conf import settings
print('THROTTLE_CLASSES:', settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_CLASSES'))
print('THROTTLE_RATES:', settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES'))
"
# Должно показать: [] и {}
```

### Проверка 2: Nginx или внешний reverse proxy

Если изменения применились, но ошибка 429 остается, п

## Если ошибка 429 сохраняется

Проблема может быть в nginx или другом reverse proxy перед Django.

### Проверить наличие nginx:

```bash
docker ps | grep nginx
docker-compose config | grep nginx
```

### Если nginx найден:

```bash
# Посмотреть конфигурацию nginx
docker-compose exec nginx cat /etc/nginx/nginx.conf | grep -A 5 "limit_req"

# Или
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf | grep -A 5 "limit_req"
```

### Отключить rate limiting в nginx:

Найдите и закомментируйте строки типа:

```nginx
# limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
# limit_req zone=mylimit burst=20 nodelay;
```

## Дополнительная проверка

### Проверить переменные окружения:

```bash
docker-compose exec web env | grep -i throttle
docker-compose exec web env | grep -i rate
```

### Проверить настройки Django:

```bash
docker-compose exec web python manage.py shell -c "
from django.conf import settings
print('DEFAULT_THROTTLE_CLASSES:', settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_CLASSES', 'Not set'))
print('DEFAULT_THROTTLE_RATES:', settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', 'Not set'))
"
```

## Результат

После выполнения всех действий throttling будет полностью отключен и ошибка 429 не должна появляться.
