# Docker окружение для Telegram бота

## Обзор

Проект полностью контейнеризирован с использованием Docker и Docker Compose. Все сервисы (бот, PostgreSQL, Redis) запускаются в отдельных контейнерах с настроенной сетью и хранилищами данных.

## Структура Docker окружения

### Сервисы

#### 1. Бот (bot)
- **Образ:** Собирается из `Dockerfile` на основе Python 3.10-slim
- **Порт:** `${WEBHOOK_PORT:-8080}` (пробрасывается из контейнера)
- **Зависимости:** PostgreSQL, Redis (с healthcheck)
- **Перезапуск:** `unless-stopped`

#### 2. PostgreSQL (postgres)
- **Образ:** `postgres:15-alpine`
- **Порт:** 5432 (пробрасывается для локальной разработки)
- **База данных:** `bot_db`
- **Пользователь:** `bot_user`
- **Пароль:** `bot_password`
- **Healthcheck:** Проверка готовности БД каждые 5 секунд
- **Volume:** `postgres_data` для сохранения данных

#### 3. Redis (redis)
- **Образ:** `redis:7-alpine`
- **Порт:** 6379 (пробрасывается для локальной разработки)
- **Healthcheck:** Проверка доступности каждые 5 секунд
- **Volume:** `redis_data` для сохранения данных

### Сеть и хранилища

- **Сеть:** `bot_network` (bridge) для изоляции сервисов
- **Volumes:** Постоянное хранение данных для PostgreSQL и Redis

## Файлы конфигурации

### Dockerfile
```dockerfile
# Используем официальный образ Python 3.10
FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY migrations/ ./migrations/

# Настройка окружения
RUN mkdir -p /app/logs
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["python", "-m", "src.main"]
```

### docker-compose.yml
Основной файл конфигурации всех сервисов с переменными окружения, healthcheck и зависимостями.

### .dockerignore
Исключает ненужные файлы из Docker контекста:
- Git файлы
- Python кэш
- Виртуальные окружения
- Логи и тесты
- Документация

## Использование

### Быстрый старт

1. **Создание файла конфигурации:**
```bash
make env
```

2. **Настройка переменных:**
```bash
vim .env
```

3. **Запуск всех сервисов:**
```bash
make up
```

4. **Применение миграций:**
```bash
make migrate
```

### Основные команды

```bash
# Сборка и запуск
make rebuild

# Перезапуск сервисов
make restart

# Просмотр логов
make logs

# Вход в контейнер бота
make shell

# Остановка сервисов
make down

# Просмотр статуса
make status
```

### Переменные окружения

#### Обязательные переменные:
- `BOT_TOKEN` - Токен Telegram бота
- `YOOKASSA_SHOP_ID` - ID магазина Yookassa
- `YOOKASSA_API_KEY` - API ключ Yookassa

#### Опциональные переменные:
- `WEBHOOK_URL` - URL для webhook (для production)
- `WEBHOOK_PATH` - Путь webhook (по умолчанию: /webhook)
- `WEBHOOK_PORT` - Порт webhook (по умолчанию: 8080)
- `ADMIN_ID` - ID администратора (по умолчанию: 0)
- `DEBUG` - Режим отладки (по умолчанию: False)
- `LOG_LEVEL` - Уровень логирования (по умолчанию: INFO)

## Разработка в Docker

### Просмотр логов
```bash
# Все логи
docker compose logs

# Логи конкретного сервиса
docker compose logs -f bot
docker compose logs -f postgres
docker compose logs -f redis
```

### Отладка
```bash
# Вход в контейнер бота
docker compose exec bot bash

# Подключение к PostgreSQL
docker compose exec postgres psql -U bot_user -d bot_db

# Подключение к Redis
docker compose exec redis redis-cli
```

### Применение миграций
```bash
# Автоматически при первом запуске (через /docker-entrypoint-initdb.d)
# Или вручную:
docker compose exec postgres psql -U bot_user -d bot_db -f /docker-entrypoint-initdb.d/0001_init.sql
```

## Production развертывание

### Настройка webhook

1. **Установите переменные окружения:**
```bash
WEBHOOK_URL=https://your-domain.com
WEBHOOK_PORT=443  # или 8080 с реверс-прокси
```

2. **Настройте реверс-прокси (Nginx):**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location /webhook {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Запустите сервисы:**
```bash
docker compose up -d
```

### Резервное копирование

```bash
# Резервное копирование PostgreSQL
docker compose exec postgres pg_dump -U bot_user bot_db > backup.sql

# Восстановление PostgreSQL
docker compose exec -T postgres psql -U bot_user bot_db < backup.sql

# Резервное копирование Redis
docker compose exec redis redis-cli BGSAVE
```

## Мониторинг

### Healthcheck
Все сервисы имеют настроенные healthcheck:
- PostgreSQL: `pg_isready` каждые 5 секунд
- Redis: `redis-cli ping` каждые 5 секунд
- Бот: зависит от готовности БД и Redis

### Логи
Логи бота сохраняются в `./logs` и доступны через:
```bash
docker compose logs -f bot
```

## Troubleshooting

### Проблемы с сетью
```bash
# Проверка сети
docker network ls
docker network inspect project_bot_network

# Пересоздание сети
docker compose down
docker compose up -d
```

### Проблемы с volumes
```bash
# Проверка volumes
docker volume ls
docker volume inspect project_postgres_data

# Очистка volumes (внимание: данные будут удалены!)
docker compose down -v
```

### Пересборка образа
```bash
# Принудительная пересборка без кэша
docker compose build --no-cache
```

### Проверка переменных окружения
```bash
# Просмотр переменных в контейнере
docker compose exec bot env | grep -E "(BOT_|DATABASE_|REDIS_|YOOKASSA_)"
```

## Безопасность

1. **Не храните `.env` файл в Git**
2. **Используйте сильные пароли для PostgreSQL**
3. **Ограничьте доступ к портам в production**
4. **Используйте HTTPS для webhook**
5. **Регулярно обновляйте образы**

## Оптимизация

### Размер образа
- Используется `python:3.10-slim` для минимизации размера
- Установка зависимостей без кэша
- `.dockerignore` исключает ненужные файлы

### Производительность
- Healthcheck для быстрого определения проблем
- Правильные зависимости между сервисами
- Volume для сохранения данных между перезапусками