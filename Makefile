# Makefile для Telegram бота

.PHONY: help install deps check lint format type-test clean check-docker build up down logs shell migrate test

# Default target
help:
	@echo "Доступные команды:"
	@echo "  install     - Установка зависимостей"
	@echo "  deps        - Установка зависимостей для разработки"
	@echo "  check       - Проверка кода (flake8, mypy, black)"
	@echo "  lint        - Проверка кода через flake8"
	@echo "  format      - Форматирование кода через black"
	@echo "  type-test   - Проверка типов через mypy"
	@echo "  clean       - Очистка временных файлов"
	@echo "  check-docker- Проверка Docker окружения"
	@echo "  build       - Сборка Docker образа"
	@echo "  up          - Запуск сервисов через docker-compose"
	@echo "  down        - Остановка сервисов"
	@echo "  logs        - Просмотр логов"
	@echo "  shell       - Вход в контейнер бота"
	@echo "  migrate     - Применение миграций"
	@echo "  test        - Запуск тестов"

# Установка зависимостей
install:
	pip install -r requirements.txt

# Установка зависимостей для разработки
deps:
	pip install -r requirements.txt
	pip install flake8 mypy black isort pytest pytest-asyncio

# Проверка кода
check: lint type-test format-check

# Проверка кода через flake8
lint:
	flake8 src/ --max-line-length=88 --ignore=E203,W503

# Форматирование кода
format:
	black src/ --line-length=88
	isort src/

# Проверка форматирования
format-check:
	black src/ --line-length=88 --check
	isort src/ --check-only

# Проверка типов
type-test:
	mypy src/ --ignore-missing-imports

# Очистка временных файлов
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# Проверка Docker окружения
check-docker:
	./check-docker.sh

# Сборка Docker образа
build:
	docker compose build

# Запуск сервисов
up:
	docker compose up -d

# Остановка сервисов
down:
	docker compose down

# Перезапуск сервисов
restart: down up

# Просмотр логов
logs:
	docker compose logs -f bot

# Вход в контейнер бота
shell:
	docker compose exec bot bash

# Применение миграций
migrate:
	docker compose exec postgres psql -U bot_user -d bot_db -f /docker-entrypoint-initdb.d/0001_init.sql

# Применение миграций локально
migrate-local:
	psql $$DATABASE_URL -f migrations/0001_init.sql

# Запуск тестов
test:
	pytest tests/ -v

# Запуск бота локально
run:
	python -m src.main

# Проверка состояния сервисов
status:
	docker compose ps

# Полная пересборка и запуск
rebuild: clean build up

# Создание файла .env из примера
env:
	cp .env.example .env
	@echo "Файл .env создан. Отредактируйте его с вашими настройками."