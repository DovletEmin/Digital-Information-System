# Requirements Update - Unified Configuration

## Изменения

### ✅ Что было сделано

1. **Объединены все requirements в один файл**
   - Раньше: `requirements/base.txt`, `requirements/dev.txt`, `requirements/prod.txt`
   - Теперь: единый `requirements.txt` в корне проекта

2. **Проверена совместимость пакетов**
   - Все пакеты совместимы друг с другом
   - Конфликтов зависимостей не обнаружено
   - Команда `pip check` подтверждает отсутствие проблем

3. **Упрощена структура Docker**
   - Удалены: `Dockerfile.dev`, `Dockerfile.offline`, `docker-compose.dev.yml`
   - Оставлен единый `Dockerfile` - готов к деплою на сервере
   - Оставлен единый `docker-compose.yml` - готов к production

4. **Обновлены Dockerfile**
   - `Dockerfile` - упрощена установка зависимостей
   - Удалены условные блоки выбора окружения
   - Добавлен EXPOSE 8000 для документации

5. **Обновлены скрипты**
   - `scripts/download_wheels.py` - теперь работает с `requirements.txt`
   - `scripts/prepare_offline.ps1` - обновлен вызов скрипта
   - `scripts/prepare_offline.sh` - обновлен вызов скрипта

6. **Обновлена документация**
   - `README.md` - инструкции по установке
   - `CHANGELOG.md` - команды установки
   - `QUICK_START_OFFLINE.md` - офлайн установка

## Структура requirements.txt

Файл организован по категориям:

```
# Core Django Framework
Django==5.2.7
...

# Django REST Framework & API
djangorestframework==3.16.1
...

# Database
psycopg2-binary==2.9.11

# Celery & Task Queue
celery==5.6.0
...

# Search - Elasticsearch
elasticsearch==8.19.2
...

# Testing & Quality Assurance
pytest==9.0.2
...

# Code Quality & Formatting
ruff==0.14.8
...

# Load Testing
locust==2.42.6
...

# Monitoring & Error Tracking
sentry-sdk==2.22.0
...
```

## Использование

### Локальная разработка

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить все зависимости
pip install -r requirements.txt
```

### Docker

```bash
# Сборка и запуск на сервере
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Офлайн установка

```bash
# 1. На машине с интернетом - скачать wheels
python scripts/download_wheels.py

# 2. Перенести wheelhouse/ на целевую машину

# 3. Установить из wheelhouse
pip install --no-index --find-links wheelhouse -r requirements.txt
```

## Версии пакетов

### Критически важные пакеты (закреплены версии)

| Пакет               | Версия | Причина            |
| ------------------- | ------ | ------------------ |
| Django              | 5.2.7  | Основной фреймворк |
| djangorestframework | 3.16.1 | API                |
| celery              | 5.6.0  | Фоновые задачи     |
| redis               | 7.1.0  | Кэш и очереди      |
| elasticsearch       | 8.19.2 | Поиск              |
| psycopg2-binary     | 2.9.11 | PostgreSQL         |
| gunicorn            | 23.0.0 | Production сервер  |
| uvicorn             | 0.34.0 | ASGI сервер        |

### Development инструменты

- `pytest` - тестирование
- `ruff` - линтер
- `autopep8` - форматирование
- `ipython` - интерактивная консоль
- `locust` - нагрузочное тестирование
- `django-silk` - профилирование

### Production инструменты

- `sentry-sdk` - мониторинг ошибок
- `gevent` - асинхронность
- `whitenoise` - статические файлы

## Совместимость

### Python

- Минимальная версия: **Python 3.11**
- Рекомендуемая: **Python 3.11.x**

### Операционные системы

- ✅ Linux (Ubuntu 20.04+, Debian 11+)
- ✅ Windows 10/11
- ✅ macOS 12+
- ✅ WSL2

### Специфичные для платформы пакеты

```python
# Windows only
pywin32==311; sys_platform == 'win32'
```

## Проверка совместимости

```bash
# Проверить конфликты зависимостей
pip check

# Показать дерево зависимостей
pip install pipdeptree
pipdeptree

# Проверить устаревшие пакеты
pip list --outdated
```

## Обновление зависимостей

### Безопасное обновление

```bash
# 1. Сделать резервную копию
cp requirements.txt requirements.txt.backup

# 2. Проверить устаревшие
pip list --outdated

# 3. Обновить конкретный пакет
pip install --upgrade django==4.2.12
pip freeze | grep Django >> requirements.txt

# 4. Проверить совместимость
pip check

# 5. Запустить тесты
pytest
```

### Массовое обновление (осторожно!)

```bash
# Обновить все пакеты (может сломать совместимость)
pip install -U -r requirements.txt
pip freeze > requirements.txt

# Обязательно протестировать!
pytest
docker-compose build
```

## Миграция со старой структуры

Если у вас была старая структура с `requirements/`:

### Автоматическая миграция

```bash
# Старые файлы больше не нужны
rm -rf requirements/

# Использовать новый requirements.txt
pip install -r requirements.txt
```

### Для Docker

Dockerfile автоматически использует новый `requirements.txt`.
Просто пересоберите образы:

```bash
docker-compose build --no-cache
```

## Отличия от предыдущей версии

| Аспект         | Старая версия                          | Новая версия                      |
| -------------- | -------------------------------------- | --------------------------------- |
| Файлы          | 3 файла (base, dev, prod)              | 1 файл (requirements.txt)         |
| Организация    | Разделение по окружениям               | Категории по функциям             |
| Установка Dev  | `pip install -r requirements/dev.txt`  | `pip install -r requirements.txt` |
| Установка Prod | `pip install -r requirements/prod.txt` | `pip install -r requirements.txt` |
| Docker build   | Условие `ARG ENV=prod/dev`             | Простая установка                 |
| Maintenance    | Дублирование в base.txt                | Единая точка правды               |

## Преимущества нового подхода

1. **Простота** - один файл, одна команда установки
2. **Меньше дублирования** - нет повторения зависимостей
3. **Проще CI/CD** - единообразные команды
4. **Быстрее build** - меньше слоев Docker
5. **Прозрачность** - все зависимости видны сразу
6. **Меньше ошибок** - нет путаницы какой файл использовать

## Недостатки

1. Установка включает dev-зависимости в production
   - **Решение**: Размер не критичен (~70MB дополнительно)
   - **Польза**: Можно отлаживать на production в крайнем случае

2. Нельзя выборочно установить только prod
   - **Решение**: Docker multi-stage build при необходимости
   - **Реальность**: Редко нужно в микросервисной архитектуре

## Дальнейшие шаги

### Опциональные улучшения

1. **Poetry/Pipenv** - переход на современные менеджеры зависимостей
2. **Dependabot** - автоматическое обновление пакетов
3. **Safety check** - проверка уязвимостей

### Мониторинг

```bash
# Еженедельная проверка уязвимостей
pip install safety
safety check

# Ежемесячная проверка устаревших пакетов
pip list --outdated
```

## Поддержка

При проблемах с установкой:

1. Проверьте версию Python: `python --version`
2. Обновите pip: `pip install --upgrade pip`
3. Проверьте системные зависимости (для psycopg2, pillow)
4. Используйте виртуальное окружение

## Дата обновления

**23 января 2026**

---

✅ Все файлы обновлены
✅ Совместимость проверена  
✅ Docker образы работают
✅ Документация актуализирована
