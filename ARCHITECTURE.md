# Архитектура Telegram бота

## Общий обзор

Это документ описывает архитектуру Telegram бота на базе Aiogram 3.x с полным циклом обработки сценариев.

## Слои архитектуры

```
┌─────────────────────────────────────────┐
│         Telegram Bot API                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Aiogram 3.x (Dispatcher)           │
│  ┌────────────────────────────────────┐ │
│  │     Handlers (Routers)             │ │
│  │  ├── commands.py                   │ │
│  │  ├── scenarios.py                  │ │
│  │  └── admin.py                      │ │
│  └────────────────────────────────────┘ │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Services & Business Logic          │
│  ┌────────────────────────────────────┐ │
│  │     ScenarioService                │ │
│  │  └── play_scenario_steps()         │ │
│  │  └── _handle_question()            │ │
│  │  └── _play_step()                  │ │
│  └────────────────────────────────────┘ │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Data Access Layer (Repositories)   │
│  ├── UserRepository                     │
│  ├── ReadingRepository                  │
│  ├── StepRepository                     │
│  ├── QuestionRepository                 │
│  └── PaymentRepository                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Database Layer                     │
│  ├── Connection Pooling (asyncpg)       │
│  ├── Query Execution                    │
│  └── Transaction Management             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL Database                │
│  ├── bot_users                          │
│  ├── readings                           │
│  ├── steps                              │
│  ├── questions                          │
│  └── payments                           │
└─────────────────────────────────────────┘
```

## Компоненты

### 1. Точка входа (main.py)

**BotManager класс:**
- Инициализирует бота
- Управляет диспетчером
- Поддерживает polling и webhook
- Обрабатывает shutdown

```python
class BotManager:
    async def initialize()      # Инициализация
    async def start_polling()   # Режим разработки
    async def start_webhook_server()  # Режим production
    async def shutdown()        # Корректное завершение
```

### 2. Обработчики команд (handlers/)

#### 2.1 Basic Commands (commands.py)

```
/start  →  Check User  →  Create if needed  →  Get Balance  →  Send Message
/help   →  Send Help
/cancel →  Cancel Operation
```

**Процесс /start:**
```
1. Extract telegram_id from message
2. Query UserRepository.get_by_telegram_id()
3. If not found:
   - Create UserCreate object
   - Call UserRepository.create()
4. Get balance via ScenarioService.get_user_balance()
5. Format and send message with balance
6. Log all actions
```

#### 2.2 Scenario Commands (scenarios.py)

```
/read [type]  →  Check User  →  Start Scenario  →  Play Steps
                                                    ├── Send Text
                                                    ├── Send Photo
                                                    └── Handle Questions
                                                        ├── Text Input
                                                        ├── Single Choice
                                                        └── Multiple Choice
```

**Процесс /read:**
```
1. Extract payload from command
2. Check/create user
3. Call ScenarioService.start_scenario()
   - Creates ReadingCreate object
   - Inserts into DB, returns Reading ID
4. Call ScenarioService.play_scenario_steps()
   - Gets all active steps (is_active=TRUE)
   - For each step:
     a. Send description text
     b. Handle photos (if image_file_id:)
     c. Get questions for step
     d. Handle each question
     e. Extract and apply delay (if delay_sec:)
5. Update reading status to "completed"
6. Send completion message
```

#### 2.3 Admin Commands (admin.py)

```
/get_photo_id  →  Check Admin  →  Wait for Photo  →  Extract file_id  →  Send to Admin
/stats         →  Check Admin  →  Get Statistics  →  Send Stats
/test_scenario →  Check Admin  →  Send Test Info
```

**Admin Authorization:**
```python
def is_admin(user_id: int) -> bool:
    return settings.admin_id > 0 and user_id == settings.admin_id
```

### 3. Сервис сценариев (ScenarioService)

**Основной сервис для проигрывания:**

```python
class ScenarioService:
    get_user_balance()
    start_scenario()
    play_scenario_steps()
    _play_step()
    _handle_question()
    _send_single_choice_question()
    _send_multiple_choice_question()
```

**Сценарий проигрывания шага:**

```
Step with description and questions:
│
├─ Text/Photo Extraction
│  ├─ If contains "image_file_id:" → Extract and send photo
│  ├─ If contains "delay_sec:" → Extract delay
│  └─ Send remaining text
│
├─ Get Questions for Step
│  └─ For each question:
│     ├─ If type="text" → Send text prompt
│     ├─ If type="single_choice" → Send inline buttons
│     └─ If type="multiple_choice" → Send keyboard buttons
│
└─ Apply Delay
   └─ asyncio.sleep(delay_sec)
```

### 4. Репозитории (Repository Pattern)

Каждый репозиторий обеспечивает изоляцию от БД:

```
Handler
  ↓
Service (ScenarioService)
  ↓
Repository (UserRepository, ReadingRepository, etc.)
  ↓
Database Layer (fetch_one, fetch_many, execute_query)
  ↓
PostgreSQL
```

**Типичный метод репозитория:**

```python
@staticmethod
async def create(data: CreateModel) -> Model:
    try:
        query = "INSERT INTO table ..."
        result = await fetch_one(query, *args)
        logger.info(f"Created: {result}")
        return Model(**result)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise RuntimeError(f"Error: {str(e)}")
```

### 5. Слой БД (Database Layer)

**Функции:**
- `init_database()` - Инициализация пула соединений
- `close_database()` - Закрытие пула
- `fetch_one()` - Получить одну запись
- `fetch_many()` - Получить несколько записей
- `execute_query()` - Выполнить запрос
- `execute_transaction()` - Выполнить транзакцию

**Connection Pool:**
```
asyncpg.Pool(
    min_size=5,
    max_size=20,
    host, port, user, password, database
)
```

### 6. Модели данных (Pydantic Models)

**User Model:**
```
User (из БД)
├── id
├── telegram_id (UQ)
├── first_name
├── last_name
├── username
├── is_bot
├── created_at
└── updated_at

UserCreate (для создания)
├── telegram_id
├── first_name
├── last_name
├── username
└── is_bot

UserUpdate (для обновления)
├── first_name?
├── last_name?
├── username?
└── is_bot?
```

## Поток данных

### Сценарий 1: /start Команда

```
User sends /start
  ↓
Handler: cmd_start()
  ├─ Get telegram_id from message
  ├─ UserRepository.get_by_telegram_id(telegram_id)
  │   ├─ Check DB → Found? Return User : None
  ├─ If None:
  │   └─ UserRepository.create(UserCreate)
  │       ├─ Execute INSERT query
  │       └─ Return new User
  ├─ ScenarioService.get_user_balance(user.id)
  │   ├─ ReadingRepository.get_by_user_id()
  │   ├─ Count free/paid readings
  │   └─ Return balance dict
  ├─ Format welcome message with balance
  └─ Send message to user
```

### Сценарий 2: /read tarot Команда

```
User sends /read tarot
  ↓
Handler: cmd_read()
  ├─ Extract payload="tarot" from message
  ├─ Get/create user (как в /start)
  ├─ ScenarioService.start_scenario(user.id, "tarot")
  │   └─ ReadingRepository.create(ReadingCreate)
  │       ├─ INSERT into readings with type="tarot"
  │       └─ Return Reading(id=1)
  ├─ ScenarioService.play_scenario_steps(user.id, chat.id, 1)
  │   ├─ StepRepository.get_active_steps()
  │   │   └─ SELECT * FROM steps WHERE is_active=TRUE
  │   │       ORDER BY step_order
  │   │       → [Step1, Step2, Step3]
  │   │
  │   ├─ For each step:
  │   │   ├─ _play_step(chat_id, step, reading_id)
  │   │   │   ├─ QuestionRepository.get_by_step_id(step.id)
  │   │   │   │   └─ SELECT * FROM questions
  │   │   │   │       WHERE step_id=step.id
  │   │   │   │       → [Q1, Q2, Q3]
  │   │   │   ├─ Send step description
  │   │   │   ├─ Extract/send photo if exists
  │   │   │   ├─ For each question:
  │   │   │   │   └─ _handle_question()
  │   │   │   │       ├─ If type="text": send prompt
  │   │   │   │       ├─ If type="single_choice": send inline buttons
  │   │   │   │       └─ If type="multiple_choice": send keyboard
  │   │   │   └─ Extract and apply delay
  │   │   └─ asyncio.sleep(delay)
  │   │
  │   ├─ ReadingRepository.update(reading_id, "completed")
  │   │   └─ UPDATE readings SET status='completed'
  │   └─ Return True
  │
  └─ Send completion message
```

### Сценарий 3: Ответ на вопрос (Callback)

```
User clicks on inline button (answer_2_red)
  ↓
Handler: answer_question()
  ├─ Parse callback data: answer_2_red
  │   ├─ question_id = 2
  │   └─ payload = red
  ├─ Log action
  ├─ Send confirmation
  │   └─ ✅ Ваш ответ: red
  └─ [Optional] Save answer to reading_payload
```

## Конфигурация и окружение

**Файл конфигурации (.env):**
```
BOT_TOKEN=123:ABCdef...      # Телеграм токен
ADMIN_ID=987654321           # ID администратора
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
YOOKASSA_SHOP_ID=...
YOOKASSA_API_KEY=...
DEBUG=False
LOG_LEVEL=INFO
```

**Загрузка конфигурации:**
```python
# src/config.py
settings = Settings()  # Pydantic validates all fields

# src/main.py
from src.config import settings
# Все параметры доступны как settings.bot_token, settings.admin_id и т.д.
```

## Логирование

**Формат:**
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Примеры:**
```
2024-01-15 10:30:45,123 - src.handlers.commands - INFO - Пользователь 123456789 запустил /start
2024-01-15 10:30:46,234 - src.services.user_repository - INFO - Создан пользователь с telegram_id: 123456789
2024-01-15 10:30:47,345 - src.services.scenario_service - INFO - Запущен сценарий 1 для пользователя 1 типа default
```

**Уровни логирования:**
- DEBUG: Переменные, состояния, детали
- INFO: Действия пользователей, операции БД
- WARNING: Предупреждения, неудачные попытки доступа
- ERROR: Ошибки, исключения
- CRITICAL: Критические отказы

## Безопасность

### 1. SQL Injection Prevention

**Используется параметризованные запросы:**
```python
# ❌ Небезопасно
query = f"SELECT * FROM users WHERE telegram_id = {user_id}"

# ✅ Безопасно
query = "SELECT * FROM users WHERE telegram_id = $1"
result = await fetch_one(query, user_id)
```

### 2. Admin Authorization

```python
def is_admin(user_id: int) -> bool:
    return settings.admin_id > 0 and user_id == settings.admin_id

if not is_admin(message.from_user.id):
    await message.answer(messages.ADMIN_ONLY)
    return
```

### 3. Error Handling

Все обработчики имеют try-except блоки:
```python
try:
    # Основной код
except Exception as e:
    logger.error(f"Ошибка: {str(e)}")
    await message.answer(messages.ERROR_MESSAGE)
```

## Расширяемость

### Добавление нового обработчика

```python
# 1. Создать новый файл src/handlers/new_handler.py
from aiogram import Router, types

router = Router()

@router.message(Command("new_command"))
async def cmd_new(message: types.Message) -> None:
    await message.answer("Ответ")

# 2. Зарегистрировать в src/handlers/__init__.py
from .new_handler import router as new_router
router.include_router(new_router)
```

### Добавление нового сервиса

```python
# 1. Создать src/services/my_service.py
class MyService:
    @staticmethod
    async def my_method(param: int) -> str:
        return "result"

# 2. Использовать в обработчике
from src.services.my_service import MyService
result = await MyService.my_method(42)
```

### Добавление нового типа вопроса

```python
# 1. В ScenarioService добавить обработчик
elif question.question_type == "new_type":
    await self._send_new_type_question(chat_id, question)

# 2. Реализовать метод
async def _send_new_type_question(self, chat_id: int, question):
    # Логика отправки вопроса
    pass
```

## Производительность

### Оптимизации

1. **Connection Pooling:**
   - asyncpg пул с 5-20 соединениями
   - Переиспользование соединений

2. **Async/Await:**
   - Все I/O операции асинхронные
   - Не блокирует обработку других пользователей

3. **Кеширование:**
   - Можно использовать Redis для кеша
   - Для часто запрашиваемых данных

4. **Pagination:**
   - Репозитории поддерживают limit/offset
   - Предотвращает загрузку всех данных

### Метрики

**Команда /start:**
- Time: ~100-200ms
- DB queries: 1-2

**Команда /read:**
- Time: ~500ms - 10s (в зависимости от количества шагов)
- DB queries: 2 + (количество шагов)

## Тестирование

### Ручное тестирование

См. `HANDLERS_TESTING_PLAN.md` для подробного плана.

### Автоматизированное тестирование

```python
# Будущее: unit tests с pytest
# Будущее: integration tests с testcontainers

pytest tests/
```

## Деплоймент

### Development (Polling)

```bash
python -m src.main
```

### Production (Webhook)

```bash
# 1. Отредактировать src/main.py
await bot_manager.start_webhook_server(host="0.0.0.0", port=8080)

# 2. Запустить через gunicorn или systemd
python -m src.main
```

## Мониторинг

**Что логируется:**
- Все команды пользователей
- Создание/обновление пользователей
- Начало/завершение сценариев
- Ошибки и исключения
- Попытки неавторизованного доступа

**Рекомендуемые инструменты:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Sentry для отслеживания ошибок
- Prometheus для метрик

## Заключение

Архитектура построена на:
- **Слоистости** - четкое разделение ответственности
- **Асинхронности** - все I/O операции асинхронные
- **Безопасности** - параметризованные запросы, проверка доступа
- **Расширяемости** - легко добавлять новые функции
- **Логировании** - полное отслеживание действий на русском

Это позволяет легко масштабировать и поддерживать бота.
