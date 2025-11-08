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

## Установка

### Требования
- Python 3.11 или выше
- pip (менеджер пакетов Python)
- PostgreSQL (опционально, для использования БД)
- Redis (опционально, для кеширования)

### Шаги установки

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
pip install -r requirements.txt
```

4. **Создание файла конфигурации:**
```bash
cp .env.example .env
```

5. **Заполнение переменных окружения:**
Отредактируйте файл `.env` и установите следующие значения:
- `BOT_TOKEN` - токен вашего Telegram бота (получить на @BotFather)
- `DATABASE_URL` - URL для подключения к PostgreSQL (если используется)
- `REDIS_URL` - URL для подключения к Redis (если используется)
- `YOOKASSA_SHOP_ID` - ID магазина в Yookassa
- `YOOKASSA_API_KEY` - API ключ Yookassa
- `WEBHOOK_URL` - URL вашего сервера для webhook (для production)

6. **Применение миграций базы данных:**
Примените начальную миграцию для создания таблиц:
```bash
psql $DATABASE_URL -f migrations/0001_init.sql
```

Подробная документация по миграциям: [migrations/README.md](migrations/README.md)

## Запуск

### Режим разработки (Polling)

```bash
python -m src.main
```

### Режим webhook (Production)

1. Отредактируйте `src/main.py` и замените `await bot_manager.start_polling()` на `await bot_manager.start_webhook_server()`

2. Запустите бота:
```bash
python -m src.main
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
pip install -r requirements.txt
```

### Запуск с горячей перезагрузкой

Для удобства разработки можно использовать `watchdog`:

```bash
pip install watchdog
python -m watchdog.auto_reload src/main.py
```

## Лицензия

MIT

## Поддержка

Если у вас возникли проблемы при установке или запуске, пожалуйста, создайте issue в репозитории.
