# Makefile for SMU Digital Library
# Convenient commands for development and deployment

.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test lint format clean

help:
	@echo "SMU Digital Library - Available Commands"
	@echo ""
	@echo "  make build           - Build Docker images"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - Show logs (all services)"
	@echo "  make logs-web        - Show web service logs"
	@echo "  make shell           - Open Django shell"
	@echo "  make bash            - Open bash in web container"
	@echo "  make migrate         - Run database migrations"
	@echo "  make makemigrations  - Create new migrations"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linter (ruff)"
	@echo "  make format          - Format code"
	@echo "  make clean           - Remove containers and volumes"
	@echo "  make backup-db       - Backup database"
	@echo "  make restore-db      - Restore database from backup"
	@echo "  make download-wheels - Download all wheels (dev)"
	@echo "  make download-wheels-all - Download all wheels (base+dev+prod)"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started! Access:"
	@echo "  - API: http://localhost:8000/api/v1/"
	@echo "  - Admin: http://localhost:8000/admin/"
	@echo "  - Docs: http://localhost:8000/api/docs/swagger/"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-celery:
	docker-compose logs -f celery-worker

shell:
	docker-compose exec web python manage.py shell

bash:
	docker-compose exec web bash

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

test:
	docker-compose exec web pytest

test-cov:
	docker-compose exec web pytest --cov=content --cov-report=html

lint:
	docker-compose exec web ruff check .

format:
	docker-compose exec web autopep8 --in-place --recursive .

clean:
	docker-compose down -v
	@echo "Removed containers and volumes"

backup-db:
	@mkdir -p backups
	@echo "Creating database backup..."
	docker-compose exec -T db pg_dump -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) $(shell grep POSTGRES_DB .env | cut -d '=' -f2) > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created in backups/"

restore-db:
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T db psql -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) $(shell grep POSTGRES_DB .env | cut -d '=' -f2) < $$backup_file

flush-views:
	docker-compose exec web python manage.py flush_views

rebuild-search:
	docker-compose exec web python manage.py search_index --rebuild

# Production commands
prod-build:
	docker build --build-arg ENV=prod -t smu-library:prod .

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

# Development setup
dev-setup:
	cp .env.example .env
	@echo "Created .env file. Please edit it with your settings."
	@echo "Generate SECRET_KEY with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""

# Wheelhouse management
download-wheels:
	python scripts/download_wheels.py --env dev

download-wheels-base:
	python scripts/download_wheels.py --env base

download-wheels-prod:
	python scripts/download_wheels.py --env prod

download-wheels-all:
	python scripts/download_wheels.py --all
