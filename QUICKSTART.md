# SMU Library - Быстрый старт 🚀

## Для локальной разработки

```bash
# 1. Клонировать
git clone <repo-url>
cd smu-library

# 2. Настроить .env
cp .env.example .env

# 3. Запустить
docker-compose up -d --build

# 4. Создать админа
docker-compose exec web python manage.py createsuperuser

# Готово! Открыть http://localhost:8000/api/v1/
```

## Для деплоя на сервере

```bash
# 1. На сервере
git clone <repo-url>
cd smu-library

# 2. Настроить production .env
nano .env
# DEBUG=False
# SECRET_KEY=<генерировать: python -c "import secrets; print(secrets.token_urlsafe(50))">
# ALLOWED_HOSTS=your-domain.com

# 3. Запустить
docker-compose up -d --build

# 4. Создать админа
docker-compose exec web python manage.py createsuperuser

# Готово!
```

## Полезные команды

```bash
# Логи
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Миграции
docker-compose exec web python manage.py migrate

# Бэкап БД
docker-compose exec db pg_dump -U smu smu > backup.sql
```

## Документация

- [DEPLOY.md](DEPLOY.md) - Подробная инструкция по деплою
- [README.md](README.md) - Полная документация
- [SIMPLIFICATION_SUMMARY.md](SIMPLIFICATION_SUMMARY.md) - Что изменилось

## Структура (упрощенная)

```
smu-library/
├── docker-compose.yml    # ← Один файл для запуска всего
├── Dockerfile           # ← Один образ для всего
├── requirements.txt     # ← Все зависимости
└── .env                 # ← Конфигурация
```

✅ **Просто. Быстро. Работает.**
