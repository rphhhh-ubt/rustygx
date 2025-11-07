# Сводка по миграции 0001_init.sql

## Общая информация

**Файл:** `0001_init.sql`  
**Описание:** Инициализация базы данных для Telegram бота  
**Дата создания:** Ноябрь 2024

## Созданные таблицы

### 1. bot_users
Пользователи Telegram бота
- **Первичный ключ:** id (SERIAL)
- **Уникальные поля:** telegram_id (BIGINT)
- **Обязательные поля:** telegram_id, first_name, is_bot, created_at, updated_at
- **Опциональные поля:** last_name, username
- **Значения по умолчанию:** is_bot (FALSE), created_at (NOW()), updated_at (NOW())

**Индексы:**
- `idx_bot_users_telegram_id` на telegram_id
- `idx_bot_users_username` на username (WHERE username IS NOT NULL)
- `idx_bot_users_created_at` на created_at

---

### 2. readings
Записи чтений/сессий пользователей
- **Первичный ключ:** id (SERIAL)
- **Внешние ключи:** user_id → bot_users.id (CASCADE DELETE/UPDATE)
- **Обязательные поля:** user_id, reading_type, reading_payload, status, created_at
- **Опциональные поля:** completed_at
- **Значения по умолчанию:** reading_payload ('{}'), status ('pending'), created_at (NOW())

**Индексы:**
- `idx_readings_user_id` на user_id
- `idx_readings_status` на status
- `idx_readings_created_at` на created_at (DESC)
- `idx_readings_reading_type` на reading_type
- `idx_readings_payload_gin` GIN индекс на reading_payload (для JSONB запросов)

**Каскадные правила:**
- При удалении пользователя удаляются все его readings
- При обновлении id пользователя обновляется user_id в readings

---

### 3. steps
Шаги в процессе (онбординг, обучение, опросы)
- **Первичный ключ:** id (SERIAL)
- **Уникальные поля:** step_order (INTEGER)
- **Обязательные поля:** name, step_order, is_active, created_at, updated_at
- **Опциональные поля:** description
- **Значения по умолчанию:** is_active (TRUE), created_at (NOW()), updated_at (NOW())

**Индексы:**
- `idx_steps_order` на step_order
- `idx_steps_active` на is_active (WHERE is_active = TRUE)

---

### 4. questions
Вопросы для шагов процесса
- **Первичный ключ:** id (SERIAL)
- **Внешние ключи:** step_id → steps.id (CASCADE DELETE/UPDATE)
- **Обязательные поля:** step_id, question_text, question_type, question_order, is_required, created_at, updated_at
- **Опциональные поля:** -
- **Значения по умолчанию:** question_type ('text'), options ('[]'), is_required (TRUE), created_at (NOW()), updated_at (NOW())

**Индексы:**
- `idx_questions_step_id` на step_id
- `idx_questions_order` на (step_id, question_order)
- `idx_questions_options_gin` GIN индекс на options (для JSONB запросов)
- `idx_questions_step_order_unique` UNIQUE на (step_id, question_order)

**Каскадные правила:**
- При удалении шага удаляются все связанные вопросы
- При обновлении id шага обновляется step_id в questions

**Ограничения:**
- Уникальность пары (step_id, question_order) - в рамках одного шага не может быть вопросов с одинаковым порядковым номером

---

### 5. payments
Платежи пользователей через Yookassa
- **Первичный ключ:** id (SERIAL)
- **Внешние ключи:** user_id → bot_users.id (CASCADE DELETE/UPDATE)
- **Уникальные поля:** yookassa_payment_id (VARCHAR)
- **Обязательные поля:** user_id, amount, currency, status, created_at, updated_at
- **Опциональные поля:** yookassa_payment_id, description
- **Значения по умолчанию:** currency ('RUB'), status ('pending'), metadata ('{}'), created_at (NOW()), updated_at (NOW())

**Индексы:**
- `idx_payments_user_id` на user_id
- `idx_payments_status` на status
- `idx_payments_created_at` на created_at (DESC)
- `idx_payments_yookassa_id` на yookassa_payment_id (WHERE yookassa_payment_id IS NOT NULL)
- `idx_payments_metadata_gin` GIN индекс на metadata (для JSONB запросов)

**Каскадные правила:**
- При удалении пользователя удаляются все его платежи
- При обновлении id пользователя обновляется user_id в payments

**Ограничения:**
- amount > 0 (CHECK constraint)

---

## Функции и триггеры

### Функция: update_updated_at_column()
Автоматически обновляет поле `updated_at` при изменении записи.

**Используется в триггерах:**
- `trigger_bot_users_updated_at` (таблица bot_users)
- `trigger_steps_updated_at` (таблица steps)
- `trigger_questions_updated_at` (таблица questions)
- `trigger_payments_updated_at` (таблица payments)

---

## Особенности реализации

### 1. Идемпотентность
Миграция использует конструкции `IF NOT EXISTS` для всех объектов, что позволяет безопасно запускать её многократно.

### 2. Транзакционность
Все изменения выполняются в рамках одной транзакции (BEGIN...COMMIT). При ошибке все изменения откатываются.

### 3. Оптимизация запросов
- **GIN индексы** для JSONB полей (reading_payload, options, metadata) - оптимизация поиска по JSON
- **Partial индексы** (например, WHERE username IS NOT NULL) - экономия места и производительность
- **DESC индексы** на created_at для эффективной сортировки по дате

### 4. Каскадные операции
Настроены CASCADE правила для всех внешних ключей:
- `ON DELETE CASCADE` - автоматическое удаление зависимых записей
- `ON UPDATE CASCADE` - автоматическое обновление внешних ключей

### 5. Типы данных
- **BIGINT** для telegram_id (поддержка больших ID Telegram)
- **JSONB** для payload, options, metadata (эффективное хранение JSON с индексацией)
- **DECIMAL(10,2)** для amount (точное хранение денежных значений)
- **TIMESTAMP WITH TIME ZONE** для всех временных меток (поддержка часовых поясов)

### 6. Комментарии
Все таблицы и колонки имеют комментарии на русском языке (COMMENT ON).

---

## Рекомендации по использованию

### Для frequently used запросов:
1. Поиск пользователя по telegram_id - используется индекс `idx_bot_users_telegram_id`
2. Выборка readings по user_id - используется индекс `idx_readings_user_id`
3. Выборка шагов по порядку - используется индекс `idx_steps_order`
4. Выборка вопросов для шага - используется индекс `idx_questions_step_id`
5. Поиск платежей по пользователю - используется индекс `idx_payments_user_id`
6. Поиск платежа по yookassa_payment_id - используется индекс `idx_payments_yookassa_id`

### Для JSONB запросов:
```sql
-- Поиск по reading_payload
SELECT * FROM readings WHERE reading_payload @> '{"status": "completed"}';

-- Поиск по options в questions
SELECT * FROM questions WHERE options @> '[{"value": "yes"}]';

-- Поиск по metadata в payments
SELECT * FROM payments WHERE metadata @> '{"source": "telegram"}';
```

---

## Объем миграции

- **Строк кода:** 281
- **Таблиц:** 5
- **Индексов:** 18
- **Триггеров:** 4
- **Функций:** 1
- **Внешних ключей:** 3
- **JSONB полей:** 3

---

## Проверка применения

После применения миграции выполните проверку:

```sql
-- Проверка наличия таблиц
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Проверка индексов
SELECT tablename, indexname FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Проверка внешних ключей
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule,
    rc.update_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;

-- Проверка триггеров
SELECT trigger_name, event_manipulation, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;
```
