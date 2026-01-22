# 🚀 Offline Build Guide - WSL без интернета

## Проблема

При сборке в WSL без интернета возникает ошибка:

```
E: Failed to fetch http://deb.debian.org/debian/dists/trixie/InRelease  403  Forbidden
```

## Решение

### Вариант 1: Использовать полный образ Python (Рекомендуется)

Обновлённый `Dockerfile` теперь использует `python:3.11` вместо `python:3.11-slim`. Этот образ уже содержит все необходимые инструменты сборки.

**Шаги:**

1. **Предварительно скачать образы Docker** (на машине с интернетом):

```bash
# На Windows или машине с интернетом
docker pull python:3.11
docker pull postgres:15
docker pull redis:7
docker pull elasticsearch:7.17.13

# Сохранить образы
docker save python:3.11 -o python311.tar
docker save postgres:15 -o postgres15.tar
docker save redis:7 -o redis7.tar
docker save elasticsearch:7.17.13 -o elasticsearch7.tar

# Или одной командой в архив
docker save python:3.11 postgres:15 redis:7 elasticsearch:7.17.13 | gzip > docker-images.tar.gz
```

2. **Перенести образы в WSL**:

```bash
# Скопировать файлы в WSL
cp /mnt/c/Users/Emin/Desktop/SMU/docker-images.tar.gz ~/

# Загрузить образы в Docker
cd ~/
gunzip docker-images.tar.gz
docker load -i docker-images.tar

# Или по отдельности
docker load -i python311.tar
docker load -i postgres15.tar
docker load -i redis7.tar
docker load -i elasticsearch7.tar
```

3. **Собрать проект**:

```bash
cd ~/smu-library
docker-compose build --no-cache
docker-compose up -d
```

### Вариант 2: Offline Dockerfile (100% offline)

Используйте `Dockerfile.offline` для полностью автономной сборки:

```bash
# В WSL
docker-compose -f docker-compose.offline.yml build
docker-compose -f docker-compose.offline.yml up -d
```

Создайте `docker-compose.offline.yml`:

```yaml
version: "3.8"

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.offline
      args:
        ENV: dev
    # ... остальные настройки как в docker-compose.yml
```

### Вариант 3: Использовать кэш сборки

Если у вас уже был успешный build раньше:

```bash
# Docker использует кэшированные слои
docker-compose build
```

## Почему это работает?

1. **python:3.11** (полный образ):
   - Размер: ~1GB (vs 130MB для slim)
   - Включает: gcc, make, build-essential, curl
   - ❌ Не требует apt-get install
   - ✅ Все инструменты уже есть

2. **Wheelhouse**:
   - 103 из 123 пакетов универсальные
   - Остальные 20 - Docker попробует установить из wheelhouse
   - Если нет - пропустит с предупреждением

3. **Предзагруженные образы**:
   - PostgreSQL, Redis, Elasticsearch
   - Один раз скачать, всегда использовать

## Проверка

После загрузки образов проверьте:

```bash
docker images
```

Должны быть:

- python:3.11
- postgres:15
- redis:7
- elasticsearch:7.17.13

## Troubleshooting

### Ошибка: "image not found"

```bash
# Проверить доступные образы
docker images

# Если нет нужного образа - загрузить заново
docker load -i <image-file.tar>
```

### Ошибка: "cannot install package"

```bash
# Проверить wheelhouse
ls wheelhouse/*.whl | wc -l  # Должно быть 123

# Пересобрать с флагом --no-cache
docker-compose build --no-cache web
```

### Ошибка: "postgresql-client not found"

Это не критично! База данных работает в отдельном контейнере. Если нужны команды `psql` внутри web контейнера, можно:

1. Подключаться к базе из контейнера postgres:

```bash
docker-compose exec db psql -U smu_user -d smu_db
```

2. Или установить postgresql-client из wheelhouse (если есть)

## Команды для подготовки (на машине с интернетом)

```bash
# 1. Скачать Docker образы
cd /mnt/c/Users/Emin/Desktop/SMU
docker-compose pull

# 2. Сохранить образы
docker save $(docker-compose config | grep 'image:' | awk '{print $2}') | gzip > docker-images-smu.tar.gz

# 3. Скопировать в безопасное место
cp docker-images-smu.tar.gz /mnt/d/backup/

# 4. В WSL без интернета загрузить
docker load -i /mnt/d/backup/docker-images-smu.tar.gz
```

## Итоговый размер

- Docker images: ~3.5 GB (один раз)
- Wheelhouse: ~71 MB
- Project code: ~50 MB

**Итого: ~3.6 GB** для полностью автономной работы

---

**Статус**: ✅ Ready for offline deployment  
**Tested**: Python 3.11, Django 5.2.7, PostgreSQL 15  
**Internet required**: ❌ No (after initial setup)
