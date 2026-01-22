# ⚡ Quick Start - Offline Deployment в WSL

## 🎯 Проблема

WSL не имеет доступа к интернету → Docker не может скачать образы и системные пакеты.

## ✅ Решение (5 шагов)

### ⚠️ ЧАСТЬ 1: На машине С ИНТЕРНЕТОМ (Windows PowerShell - НЕ WSL!)

**ВНИМАНИЕ**: Эти команды запускаются в **Windows PowerShell**, не в WSL!  
WSL не имеет интернета, поэтому Docker образы нужно скачать в Windows.

#### Шаг 1: Скачать Docker образы

**⚠️ ВАЖНО**: Запускайте в **Windows PowerShell**, НЕ В WSL! (WSL не имеет интернета)

```powershell
# В Windows PowerShell (открыть на Windows, не в WSL!)
cd C:\Users\Emin\Desktop\SMU
.\scripts\prepare_offline.ps1   
```

Или вручную:

```powershell
docker pull python:3.11
docker pull postgres:15
docker pull redis:7
docker pull elasticsearch:7.17.13

# Сохранить в архив
docker save python:3.11 postgres:15 redis:7 elasticsearch:7.17.13 | gzip > docker-images-smu.tar.gz
```

Это создаст файл `docker-images-smu.tar.gz` (~2.5 GB)

#### Шаг 2: Подготовить wheelhouse (если ещё нет)

```powershell
# Уже сделано! У вас есть 123 пакета в wheelhouse/
```

### 🔵 ЧАСТЬ 2: В WSL (БЕЗ ИНТЕРНЕТА)

**Теперь работаем в WSL**. Docker образы уже скачаны на Windows.

#### Шаг 3: Перенести файлы в WSL

```bash
# Вариант A: Через Windows диск
cp /mnt/c/Users/Emin/Desktop/SMU/docker-images-smu.tar.gz ~/
cp -r /mnt/c/Users/Emin/Desktop/SMU ~/smu-library

# Вариант B: Через сетевую папку (если есть)
cp /mnt/d/backup/docker-images-smu.tar.gz ~/
```

#### Шаг 4: Загрузить Docker образы

```bash
cd ~
docker load -i docker-images-smu.tar.gz
```

Проверка:

```bash
docker images
# Должны увидеть:
# python:3.11
# postgres:15
# redis:7
# elasticsearch:7.17.13
```

#### Шаг 5: Собрать и запустить проект

```bash
cd ~/smu-library

# Собрать
docker-compose build

# Запустить
docker-compose up -d

# Применить миграции
docker-compose exec web python manage.py migrate

# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser
```

## 🎉 Готово!

Проверить:

```bash
curl http://localhost:8000/api/v1/
```

Или открыть в браузере:

- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- Swagger: http://localhost:8000/api/docs/swagger/

## 📊 Что занимает место?

| Компонент                | Размер      | Комментарий                 |
| ------------------------ | ----------- | --------------------------- |
| docker-images-smu.tar.gz | ~2.5 GB     | Один раз скачать            |
| wheelhouse/              | ~71 MB      | 123 Python пакета           |
| Project code             | ~50 MB      | Исходный код                |
| **Итого**                | **~2.6 GB** | Полностью автономная работа |

## 🔧 Troubleshooting

### "Cannot connect to Docker daemon"

```bash
sudo service docker start
```

### "Image not found"

```bash
# Проверить загруженные образы
docker images

# Если пусто - загрузить снова
docker load -i docker-images-smu.tar.gz
```

### "Build failed: apt-get error"

```bash
# Используйте обновлённый Dockerfile (уже исправлено)
docker-compose build --no-cache
```

### "Some packages not installed"

```bash
# Проверить wheelhouse
ls wheelhouse/*.whl | wc -l  # Должно быть 123

# Если меньше - скачать снова на машине с интернетом
pip download -r requirements/dev.txt -d wheelhouse
```

## 📝 Notes

- ✅ Dockerfile обновлён: использует `python:3.11` (не slim)
- ✅ Wheelhouse готов: 123 пакета, 103 универсальных
- ✅ Все системные зависимости опциональны
- ✅ PostgreSQL client можно установить позже если нужен

## 🚀 Автоматизация

Для повторного использования сохраните `docker-images-smu.tar.gz` на внешний диск или сетевое хранилище. При следующей установке просто:

```bash
docker load -i docker-images-smu.tar.gz
cd ~/smu-library
docker-compose up -d
```

---

**Время установки**: 10-15 минут  
**Internet required**: ❌ No  
**Works on**: Ubuntu WSL, Debian, любой Linux с Docker
