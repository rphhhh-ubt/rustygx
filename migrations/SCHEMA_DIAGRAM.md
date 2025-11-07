# Диаграмма схемы базы данных

## Визуальная структура таблиц

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE SCHEMA OVERVIEW                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐
│        bot_users (Главная)      │
├─────────────────────────────────┤
│ PK  id (SERIAL)                 │
│ UQ  telegram_id (BIGINT)        │
│     first_name (VARCHAR)        │
│     last_name (VARCHAR)         │
│     username (VARCHAR)          │
│     is_bot (BOOLEAN)            │
│     created_at (TIMESTAMPTZ)    │
│     updated_at (TIMESTAMPTZ)    │
└─────────────┬───────────────────┘
              │
              │ 1:N
              │
    ┌─────────┴────────────┬──────────────────────┐
    │                      │                      │
    │                      │                      │
    ▼                      ▼                      ▼
┌────────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│     readings       │ │    payments      │ │  (другие таблицы)    │
├────────────────────┤ ├──────────────────┤ └──────────────────────┘
│ PK  id             │ │ PK  id           │
│ FK  user_id   ───┐ │ │ FK  user_id  ───┐│
│     reading_type   │ │ │ UQ  yookassa_id  ││
│     reading_payload│ │ │     amount       ││
│     status         │ │ │     currency     ││
│     created_at     │ │ │     status       ││
│     completed_at   │ │ │     description  ││
└────────────────────┘ │ │     metadata     ││
                       │ │     created_at   ││
                       │ │     updated_at   ││
                       │ └──────────────────┘│
                       │                     │
                       └─────────────────────┘
                         CASCADE DELETE


┌─────────────────────────────────┐
│             steps               │
├─────────────────────────────────┤
│ PK  id (SERIAL)                 │
│ UQ  step_order (INTEGER)        │
│     name (VARCHAR)              │
│     description (TEXT)          │
│     is_active (BOOLEAN)         │
│     created_at (TIMESTAMPTZ)    │
│     updated_at (TIMESTAMPTZ)    │
└─────────────┬───────────────────┘
              │
              │ 1:N
              │
              ▼
┌─────────────────────────────────┐
│          questions              │
├─────────────────────────────────┤
│ PK  id (SERIAL)                 │
│ FK  step_id ──────────────────┐ │
│     question_text (TEXT)       │ │
│     question_type (VARCHAR)    │ │
│     options (JSONB)            │ │
│     question_order (INTEGER)   │ │
│     is_required (BOOLEAN)      │ │
│     created_at (TIMESTAMPTZ)   │ │
│     updated_at (TIMESTAMPTZ)   │ │
└────────────────────────────────┘ │
                                   │
                                   │
                      CASCADE DELETE


═══════════════════════════════════════════════════════════════════════════════
ЛЕГЕНДА:
═══════════════════════════════════════════════════════════════════════════════
PK  = Primary Key (Первичный ключ)
FK  = Foreign Key (Внешний ключ)
UQ  = Unique (Уникальное ограничение)
1:N = Связь один-ко-многим
```

## Связи между таблицами

### 1. bot_users → readings (1:N)
```
bot_users.id ←──[CASCADE]── readings.user_id
```
- Один пользователь может иметь много чтений
- При удалении пользователя удаляются все его чтения

### 2. bot_users → payments (1:N)
```
bot_users.id ←──[CASCADE]── payments.user_id
```
- Один пользователь может иметь много платежей
- При удалении пользователя удаляются все его платежи

### 3. steps → questions (1:N)
```
steps.id ←──[CASCADE]── questions.step_id
```
- Один шаг может иметь много вопросов
- При удалении шага удаляются все связанные вопросы
- Уникальное ограничение: (step_id, question_order) - в рамках шага вопросы упорядочены уникально

## Индексы для оптимизации

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            ИНДЕКСЫ ПО ТАБЛИЦАМ                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  bot_users:                                                             │
│    ├── idx_bot_users_telegram_id (telegram_id)                         │
│    ├── idx_bot_users_username (username WHERE username IS NOT NULL)    │
│    └── idx_bot_users_created_at (created_at)                           │
│                                                                         │
│  readings:                                                              │
│    ├── idx_readings_user_id (user_id)                                  │
│    ├── idx_readings_status (status)                                    │
│    ├── idx_readings_created_at (created_at DESC)                       │
│    ├── idx_readings_reading_type (reading_type)                        │
│    └── idx_readings_payload_gin (reading_payload) [GIN]                │
│                                                                         │
│  steps:                                                                 │
│    ├── idx_steps_order (step_order)                                    │
│    └── idx_steps_active (is_active WHERE is_active = TRUE)             │
│                                                                         │
│  questions:                                                             │
│    ├── idx_questions_step_id (step_id)                                 │
│    ├── idx_questions_order (step_id, question_order)                   │
│    ├── idx_questions_step_order_unique (step_id, question_order) [UQ]  │
│    └── idx_questions_options_gin (options) [GIN]                       │
│                                                                         │
│  payments:                                                              │
│    ├── idx_payments_user_id (user_id)                                  │
│    ├── idx_payments_status (status)                                    │
│    ├── idx_payments_created_at (created_at DESC)                       │
│    ├── idx_payments_yookassa_id (yookassa_payment_id) [PARTIAL]        │
│    └── idx_payments_metadata_gin (metadata) [GIN]                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

[GIN]     = GIN индекс для JSONB полей (эффективный поиск по JSON)
[PARTIAL] = Частичный индекс (только для NOT NULL значений)
[UQ]      = Уникальный индекс
```

## Триггеры автоматического обновления

```
┌──────────────────────────────────────────────────────────────────────┐
│              ТРИГГЕРЫ update_updated_at_column()                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  BEFORE UPDATE ON:                                                   │
│    ├── bot_users    → trigger_bot_users_updated_at                  │
│    ├── steps        → trigger_steps_updated_at                      │
│    ├── questions    → trigger_questions_updated_at                  │
│    └── payments     → trigger_payments_updated_at                   │
│                                                                      │
│  Функция: Автоматически устанавливает updated_at = NOW()            │
│           при каждом UPDATE операции                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Типы данных для специальных полей

```
┌────────────────────────────────────────────────────────────────────────┐
│                       СПЕЦИАЛЬНЫЕ ТИПЫ ДАННЫХ                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  JSONB поля (с GIN индексами):                                        │
│  ├── readings.reading_payload    - Данные чтения                      │
│  ├── questions.options            - Варианты ответов на вопрос        │
│  └── payments.metadata            - Дополнительные данные платежа     │
│                                                                        │
│  BIGINT поля:                                                          │
│  └── bot_users.telegram_id        - Большие ID из Telegram            │
│                                                                        │
│  DECIMAL поля:                                                         │
│  └── payments.amount (10,2)       - Точная сумма платежа              │
│                                                                        │
│  TIMESTAMP WITH TIME ZONE:                                             │
│  └── Все поля *_at                - Даты с учетом часового пояса      │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Ограничения (Constraints)

```
┌────────────────────────────────────────────────────────────────────────┐
│                          ОГРАНИЧЕНИЯ ДАННЫХ                            │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  UNIQUE (Уникальность):                                                │
│  ├── bot_users.telegram_id                                            │
│  ├── steps.step_order                                                 │
│  ├── payments.yookassa_payment_id                                     │
│  └── questions.(step_id, question_order)                              │
│                                                                        │
│  CHECK (Проверка значений):                                            │
│  └── payments.amount > 0                                              │
│                                                                        │
│  NOT NULL (Обязательные поля):                                         │
│  ├── Все первичные ключи (id)                                         │
│  ├── Все внешние ключи (user_id, step_id)                            │
│  ├── Базовые поля (first_name, reading_type, question_text, etc.)    │
│  └── Временные метки created_at, updated_at                           │
│                                                                        │
│  DEFAULT (Значения по умолчанию):                                      │
│  ├── bot_users.is_bot = FALSE                                         │
│  ├── readings.reading_payload = '{}'                                  │
│  ├── readings.status = 'pending'                                      │
│  ├── steps.is_active = TRUE                                           │
│  ├── questions.question_type = 'text'                                 │
│  ├── questions.options = '[]'                                         │
│  ├── questions.is_required = TRUE                                     │
│  ├── payments.currency = 'RUB'                                        │
│  ├── payments.status = 'pending'                                      │
│  ├── payments.metadata = '{}'                                         │
│  └── Все created_at, updated_at = NOW()                               │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Примеры использования схемы

### Пример 1: Создание пользователя и его первого чтения
```sql
-- Создать пользователя
INSERT INTO bot_users (telegram_id, first_name, username)
VALUES (123456789, 'Иван', 'ivan_user')
RETURNING id;

-- Создать чтение для пользователя (предположим id = 1)
INSERT INTO readings (user_id, reading_type, reading_payload, status)
VALUES (1, 'tarot', '{"cards": ["The Fool", "The Magician"], "interpretation": "..."}', 'completed');
```

### Пример 2: Создание процесса с шагами и вопросами
```sql
-- Создать шаг
INSERT INTO steps (name, description, step_order)
VALUES ('Знакомство', 'Первый шаг - знакомство с пользователем', 1)
RETURNING id;

-- Создать вопросы для шага (предположим id = 1)
INSERT INTO questions (step_id, question_text, question_type, question_order)
VALUES 
  (1, 'Как вас зовут?', 'text', 1),
  (1, 'Сколько вам лет?', 'text', 2),
  (1, 'Выберите ваш пол', 'choice', 3);

-- Добавить варианты для вопроса с выбором
UPDATE questions 
SET options = '[{"value": "male", "label": "Мужской"}, {"value": "female", "label": "Женский"}]'::JSONB
WHERE step_id = 1 AND question_order = 3;
```

### Пример 3: Создание платежа
```sql
-- Создать платеж
INSERT INTO payments (user_id, yookassa_payment_id, amount, currency, status, description)
VALUES (1, 'yookassa_abc123', 499.00, 'RUB', 'pending', 'Оплата консультации по Таро');

-- Обновить статус платежа (updated_at обновится автоматически через триггер)
UPDATE payments 
SET status = 'succeeded', metadata = '{"transaction_id": "txn_123", "method": "bank_card"}'::JSONB
WHERE yookassa_payment_id = 'yookassa_abc123';
```

### Пример 4: Получение всех данных пользователя
```sql
-- Полная информация о пользователе
SELECT 
  u.*,
  COUNT(DISTINCT r.id) as readings_count,
  COUNT(DISTINCT p.id) as payments_count,
  SUM(p.amount) FILTER (WHERE p.status = 'succeeded') as total_paid
FROM bot_users u
LEFT JOIN readings r ON u.id = r.user_id
LEFT JOIN payments p ON u.id = p.user_id
WHERE u.telegram_id = 123456789
GROUP BY u.id;
```

### Пример 5: Получение активного процесса с вопросами
```sql
-- Все активные шаги с вопросами, упорядоченные правильно
SELECT 
  s.step_order,
  s.name as step_name,
  s.description as step_description,
  q.question_order,
  q.question_text,
  q.question_type,
  q.options,
  q.is_required
FROM steps s
LEFT JOIN questions q ON s.id = q.step_id
WHERE s.is_active = TRUE
ORDER BY s.step_order, q.question_order;
```
