# Телеграм бот

Каркас асинхронного Телеграм бота на базе фреймворка Aiogram 3.x с поддержкой обработки платежей через Yookassa.

## Стек технологий

- **Aiogram 3.x** - асинхронный фреймворк для работы с Telegram Bot API
- **Python 3.11+** - язык программирования
- **AsyncPG** - асинхронный драйвер PostgreSQL
- **Pydantic** - валидация данных и управление конфигурацией
- **Yookassa** - интеграция с платежной системой
- **Redis** - кеширование и очередь задач
- **aiohttp** - асинхронный HTTP клиент

## Структура проекта

```
project/
├── src/
│   ├── handlers/        # Обработчики команд и сообщений
│   ├── services/        # Бизнес-логика и интеграции
│   ├── models/          # Модели данных
│   ├── locales/         # Локализированные сообщения
│   ├── config.py        # Конфигурация приложения
│   └── main.py          # Точка входа
├── migrations/          # SQL миграции базы данных
├── requirements.txt     # Зависимости проекта
├── .env.example         # Пример файла конфигурации
└── README.md           # Документация
```

## Быстрый старт с Docker

1. **Проверка окружения:**
```bash
make check-docker
```

2. **Создание конфигурации:**
```bash
make env
# Отредактируйте .env файл с вашими токенами
```

3. **Запуск всех сервисов:**
```bash
make up
```

4. **Применение миграций:**
```bash
make migrate
```

5. **Проверка статуса:**
```bash
make status
```

## Установка

### Требования
- Python 3.10 или выше
- Docker и Docker Compose (для запуска в контейнерах)
- pip (менеджер пакетов Python)
- PostgreSQL (опционально, для использования БД)
- Redis (опционально, для кеширования)

### Шаги установки

#### Вариант 1: Установка в Docker (рекомендуется)

1. **Клонирование репозитория:**
```bash
git clone <repository_url>
cd project
```

2. **Создание файла конфигурации:**
```bash
make env
```

3. **Заполнение переменных окружения:**
Отредактируйте файл `.env` и установите следующие значения:
- `BOT_TOKEN` - токен вашего Telegram бота (получить на @BotFather)
- `YOOKASSA_SHOP_ID` - ID магазина в Yookassa
- `YOOKASSA_API_KEY` - API ключ Yookassa
- `WEBHOOK_URL` - URL вашего сервера для webhook (для production)
- `ADMIN_ID` - Telegram ID администратора (для админ-команд)

4. **Запуск сервисов:**
```bash
make up
```

Это запустит три сервиса:
- PostgreSQL базу данных
- Redis для кеширования
- Telegram бот

5. **Применение миграций:**
```bash
make migrate
```

6. **Проверка статуса:**
```bash
make status
```

#### Вариант 2: Локальная установка

1. **Клонирование репозитория:**
```bash
git clone <repository_url>
cd project
```

2. **Создание виртуального окружения:**
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. **Установка зависимостей:**
```bash
make install
```

4. **Создание файла конфигурации:**
```bash
cp .env.example .env
```

5. **Заполнение переменных окружения:**
Отредактируйте файл `.env` и установите следующие значения:
- `BOT_TOKEN` - токен вашего Telegram бота (получить на @BotFather)
- `DATABASE_URL` - URL для подключения к PostgreSQL
- `REDIS_URL` - URL для подключения к Redis
- `YOOKASSA_SHOP_ID` - ID магазина в Yookassa
- `YOOKASSA_API_KEY` - API ключ Yookassa
- `WEBHOOK_URL` - URL вашего сервера для webhook (для production)

6. **Применение миграций базы данных:**
```bash
make migrate-local
```

Подробная документация по миграциям: [migrations/README.md](migrations/README.md)

## Запуск

### Запуск в Docker

#### Режим разработки (Polling)
```bash
# Запуск всех сервисов
make up

# Просмотр логов
make logs

# Остановка сервисов
make down
```

#### Режим webhook (Production)

1. **Настройте переменные окружения в `.env`:**
   - `WEBHOOK_URL` - URL вашего сервера
   - `WEBHOOK_PORT` - порт для webhook (по умолчанию 8080)
   - `WEBHOOK_PATH` - путь для webhook (по умолчанию /webhook)

2. **Запуск сервисов:**
```bash
make up
```

3. **Проверка работы webhook:**
```bash
# Проверка доступности порта
curl http://localhost:8080/webhook
```

### Локальный запуск

#### Режим разработки (Polling)

```bash
python -m src.main
```

#### Режим webhook (Production)

1. Отредактируйте `src/main.py` и замените `await bot_manager.start_polling()` на `await bot_manager.start_webhook_server()`

2. Запустите бота:
```bash
python -m src.main
```

## Полезные команды Docker

### Управление сервисами
```bash
# Пересборка и запуск
make rebuild

# Перезапуск
make restart

# Просмотр статуса
make status

# Вход в контейнер бота
make shell

# Применение миграций
make migrate
```

### Просмотр логов
```bash
# Все логи
docker compose logs

# Логи только бота
docker compose logs -f bot

# Логи PostgreSQL
docker compose logs -f postgres

# Логи Redis
docker compose logs -f redis
```

### Отладка
```bash
# Вход в контейнер для отладки
docker compose exec bot bash

# Подключение к базе данных
docker compose exec postgres psql -U bot_user -d bot_db

# Подключение к Redis
docker compose exec redis redis-cli
```

## Конфигурация

Все параметры конфигурации загружаются из файла `.env` с использованием Pydantic.

### Основные переменные окружения

| Переменная | Описание | Обязательная |
|-----------|---------|-------------|
| BOT_TOKEN | Токен Telegram бота | Да |
| ADMIN_ID | Telegram ID администратора (для админ-команд) | Нет |
| DATABASE_URL | URL подключения к PostgreSQL | Да |
| REDIS_URL | URL подключения к Redis | Нет |
| WEBHOOK_URL | URL вашего сервера для webhook | Нет |
| WEBHOOK_PATH | Путь для webhook (по умолчанию: /webhook) | Нет |
| WEBHOOK_PORT | Порт webhook сервера (по умолчанию: 8080) | Нет |
| YOOKASSA_SHOP_ID | ID магазина Yookassa | Да |
| YOOKASSA_API_KEY | API ключ Yookassa | Да |
| DEBUG | Режим отладки (True/False) | Нет |
| LOG_LEVEL | Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL) | Нет |

## Документация

### Реализованные обработчики

#### Основные команды

- **`/start`** - Запуск бота, проверка пользователя в БД, вывод баланса
- **`/help`** - Справка по командам
- **`/cancel`** - Отмена текущей операции

#### Команды сценариев

- **`/read [type]`** - Запуск сценария с шагами и вопросами
  - `/read` - стандартный сценарий
  - `/read tarot` - сценарий типа tarot
  - Поддерживает вопросы: текстовые, одиночный выбор (inline кнопки), множественный выбор (keyboard кнопки)
  - Поддерживает фото (image_file_id:), задержки (delay_sec:)

#### Платежные команды

- **`/buy`** - Показывает меню покупки платных чтений
  - 5 чтений - 299₽
  - 10 чтений - 499₽
  - 20 чтений - 899₽
- **`/payments`** - История платежей пользователя

#### Администраторские команды

- **`/get_photo_id`** - Получение file_id загруженного фото (только для ADMIN_ID)
- **`/stats`** - Статистика использования бота (только для ADMIN_ID)
- **`/test_scenario`** - Тестирование сценариев (только для ADMIN_ID)

**Подробная документация:** [HANDLERS_README.md](HANDLERS_README.md)

**План тестирования:** [HANDLERS_TESTING_PLAN.md](HANDLERS_TESTING_PLAN.md)

**Примеры использования:** [HANDLERS_EXAMPLES.md](HANDLERS_EXAMPLES.md)

**Интеграция YooKassa:** [YOOKASSA_INTEGRATION_README.md](YOOKASSA_INTEGRATION_README.md)

**Подробная документация по Docker:** [DOCKER_README.md](DOCKER_README.md)

**Тестирование платежей:** [YOOKASSA_TESTING_GUIDE.md](YOOKASSA_TESTING_GUIDE.md)

### Добавление новых команд

Новые команды обработчиков добавляются в файлы в директории `src/handlers/`.

Пример добавления команды:

```python
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("mycommand"))
async def cmd_my_command(message: types.Message) -> None:
    """Обработчик команды /mycommand."""
    await message.answer("Ответ на команду")
```

Не забудьте добавить маршрутизатор в `src/handlers/__init__.py`:

```python
from .my_handlers import router as my_handlers_router
router.include_router(my_handlers_router)
```

### Добавление сервисов

Сервисы с бизнес-логикой добавляются в директорию `src/services/`.

### Локализированные сообщения

Все пользовательские сообщения хранятся в `src/locales/messages.py` на русском языке.

## Логирование

Логи настраиваются в `src/main.py`. Уровень логирования управляется переменной `LOG_LEVEL` в `.env`.

Все сообщения об ошибках выводятся на русском языке.

## Разработка

### Установка зависимостей для разработки

```bash
make deps
```

### Проверка кода

Проект использует следующие инструменты для проверки качества кода:

```bash
# Полная проверка кода
make check

# Отдельные проверки
make lint          # flake8
make type-test     # mypy
make format-check  # black и isort
```

### Форматирование кода

```bash
# Форматирование кода
make format
```

### Тестирование

```bash
# Запуск тестов
make test
```

### Запуск с горячей перезагрузкой

Для удобства разработки можно использовать `watchdog`:

```bash
pip install watchdog
python -m watchdog.auto_reload src/main.py
```

### Разработка в Docker

Для разработки в контейнере используйте:

```bash
# Запуск в режиме разработки
make up

# Вход в контейнер для разработки
make shell

# Просмотр логов в реальном времени
make logs

# Перезапуск после изменений
make restart
```

## Лицензия

MIT

## Поддержка

Если у вас возникли проблемы при установке или запуске, пожалуйста, создайте issue в репозитории.
