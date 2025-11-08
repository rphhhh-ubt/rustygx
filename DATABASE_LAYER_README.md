# Слой базы данных (Database Layer)

Документация по реализованному слою базы данных для Telegram бота.

## Обзор

Слой базы данных включает в себя:
- **Модели данных** (`src/models/`) - Pydantic модели для типизации данных
- **Сервис базы данных** (`src/services/database.py`) - Управление пулом соединений asyncpg
- **Репозитории** (`src/services/*_repository.py`) - CRUD операции для каждой таблицы
- **Интеграция с приложением** - Автоматическая инициализация при запуске

## Структура

### Модели данных (`src/models/`)

#### `user.py`
- `User` - Полная модель пользователя из БД
- `UserCreate` - Модель для создания пользователя
- `UserUpdate` - Модель для обновления пользователя

#### `reading.py`
- `Reading` - Полная модель чтения из БД
- `ReadingCreate` - Модель для создания чтения
- `ReadingUpdate` - Модель для обновления чтения

#### `payment.py`
- `Payment` - Полная модель платежа из БД
- `PaymentCreate` - Модель для создания платежа
- `PaymentUpdate` - Модель для обновления платежа

#### `step.py`
- `Step` - Полная модель шага из БД
- `StepCreate` - Модель для создания шага
- `StepUpdate` - Модель для обновления шага
- `StepWithQuestions` - Модель шага с вопросами

#### `question.py`
- `Question` - Полная модель вопроса из БД
- `QuestionCreate` - Модель для создания вопроса
- `QuestionUpdate` - Модель для обновления вопроса

### Сервис базы данных (`src/services/database.py`)

Основные функции:
- `init_database()` - Инициализация пула соединений
- `close_database()` - Закрытие пула соединений
- `get_connection()` - Контекстный менеджер для получения соединения
- `execute_query()` - Выполнение запросов без возврата результата
- `fetch_one()` - Получение одной записи
- `fetch_many()` - Получение множества записей
- `fetch_val()` - Получение одного значения
- `execute_transaction()` - Выполнение транзакций
- `test_connection()` - Проверка соединения

### Репозитории

#### `UserRepository`
- `create()` - Создание пользователя
- `get_by_id()` - Получение по ID
- `get_by_telegram_id()` - Получение по telegram_id
- `get_by_username()` - Получение по username
- `update()` - Обновление данных
- `delete()` - Удаление
- `get_all()` - Получение списка с пагинацией
- `get_or_create()` - Получение или создание
- `get_total_count()` - Получение общего количества

#### `ReadingRepository`
- `create()` - Создание чтения
- `get_by_id()` - Получение по ID
- `get_by_user_id()` - Получение чтений пользователя
- `get_by_user_id_and_type()` - Получение чтений пользователя по типу
- `get_by_status()` - Получение по статусу
- `update()` - Обновление данных
- `complete_reading()` - Завершение чтения
- `delete()` - Удаление
- `get_latest_user_reading()` - Получение последнего чтения пользователя

#### `PaymentRepository`
- `create()` - Создание платежа
- `get_by_id()` - Получение по ID
- `get_by_yookassa_id()` - Получение по Yookassa ID
- `get_by_user_id()` - Получение платежей пользователя
- `get_by_status()` - Получение по статусу
- `update()` - Обновление данных
- `update_status()` - Обновление статуса
- `delete()` - Удаление
- `get_user_total_spent()` - Получение общей суммы потраченных средств
- `get_successful_payments_by_user()` - Получение успешных платежей пользователя
- `get_pending_payments()` - Получение ожидающих платежей

#### `StepRepository`
- `create()` - Создание шага
- `get_by_id()` - Получение по ID
- `get_by_order()` - Получение по порядковому номеру
- `get_active_steps()` - Получение активных шагов (отсортированных)
- `get_with_questions()` - Получение шага с вопросами
- `get_active_with_questions()` - Получение активных шагов с вопросами
- `update()` - Обновление данных
- `delete()` - Удаление
- `get_next_step_order()` - Получение следующего порядкового номера
- `reorder_steps()` - Изменение порядка шагов

#### `QuestionRepository`
- `create()` - Создание вопроса
- `get_by_id()` - Получение по ID
- `get_by_step_id()` - Получение вопросов шага (отсортированных)
- `get_by_type()` - Получение по типу
- `get_required_questions()` - Получение обязательных вопросов
- `update()` - Обновление данных
- `delete()` - Удаление
- `delete_by_step_id()` - Удаление всех вопросов шага
- `get_next_question_order()` - Получение следующего порядкового номера
- `reorder_questions()` - Изменение порядка вопросов

## Использование

### Базовые примеры

```python
from src.services import UserRepository
from src.models import UserCreate

# Создание пользователя
user_data = UserCreate(
    telegram_id=123456789,
    first_name="Иван",
    last_name="Петров",
    username="ivan_petrov"
)
user = await UserRepository.create(user_data)

# Получение пользователя
user = await UserRepository.get_by_telegram_id(123456789)

# Получение или создание
user = await UserRepository.get_or_create(123456789, user_data)
```

### Работа с платежами

```python
from src.services import PaymentRepository
from src.models import PaymentCreate
from decimal import Decimal

# Создание платежа
payment_data = PaymentCreate(
    user_id=user.id,
    amount=Decimal("499.99"),
    description="Оплата консультации",
    status="pending"
)
payment = await PaymentRepository.create(payment_data)

# Обновление статуса платежа
updated_payment = await PaymentRepository.update_status(
    payment.id, 
    "succeeded", 
    "yookassa_12345"
)

# Получение баланса пользователя
total_spent = await PaymentRepository.get_user_total_spent(user.id)
```

### Работа с шагами и вопросами

```python
from src.services import StepRepository, QuestionRepository
from src.models import StepCreate, QuestionCreate

# Получение всех активных шагов с вопросами
steps_with_questions = await StepRepository.get_active_with_questions()

for step in steps_with_questions:
    print(f"Шаг: {step.name}")
    for question in step.questions:
        print(f"  Вопрос: {question.question_text}")
```

### Транзакции

```python
from src.services import execute_transaction

# Выполнение транзакции
queries = [
    ("INSERT INTO readings (user_id, reading_type) VALUES ($1, $2) RETURNING id", (user.id, "tarot")),
    ("UPDATE users SET updated_at = NOW() WHERE id = $1", (user.id,))
]

results = await execute_transaction(queries)
```

## Конфигурация

База данных автоматически инициализируется при запуске приложения в `src/main.py`:

```python
async def initialize(self) -> None:
    # Инициализация базы данных
    await init_database()
    # ... остальная инициализация
```

И закрывается при остановке:

```python
async def shutdown(self) -> None:
    # Закрытие соединений с базой данных
    await close_database()
    # ... остальная очистка
```

## Тестирование

Для тестирования слоя базы данных используйте скрипт `test_db_layer.py`:

```bash
# Убедитесь что .env файл настроен
python test_db_layer.py
```

Скрипт проверяет:
- Соединение с базой данных
- Создание и получение пользователей
- Создание шагов и вопросов
- Создание чтений
- Создание и обновление платежей
- Получение балансов

## Обработка ошибок

Все репозитории используют единый подход к обработке ошибок:
- Логирование ошибок с русскими сообщениями
- Генерация `RuntimeError` с информативными сообщениями
- Использование параметризованных запросов для защиты от SQL-инъекций

## Производительность

- Использование пула соединений asyncpg (5-20 соединений)
- Оптимизированные запросы с индексами из миграции
- Пагинация для получения больших списков
- Кэширование соединений в контекстных менеджерах

## Локализация

Все сообщения об ошибках и логи на русском языке, что удобно для администрирования и отладки. Сообщения определены в `src/locales/messages.py`:

```python
DB_CONNECTION_ERROR = "❌ Ошибка подключения к базе данных"
DB_QUERY_ERROR = "❌ Ошибка выполнения запроса к базе данных"
DB_USER_CREATED = "✅ Пользователь успешно создан"
# ... и т.д.
```

## Безопасность

- Все запросы используют параметризованные SQL
- Проверка входных данных через Pydantic модели
- Ограничение размера пула соединений
- Таймауты выполнения запросов (60 секунд)