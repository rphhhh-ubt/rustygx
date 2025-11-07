# Миграции базы данных

Этот каталог содержит SQL миграции для базы данных PostgreSQL.

> 📚 **Полная навигация:** См. [INDEX.md](INDEX.md) для обзора всех файлов документации

## Структура

- `0001_init.sql` - Начальная миграция (создание таблиц bot_users, readings, steps, questions, payments)
- `README.md` - Основная документация (этот файл)
- `MIGRATION_SUMMARY.md` - Детальная сводка миграции
- `SCHEMA_DIAGRAM.md` - Визуальные диаграммы схемы базы данных
- `INDEX.md` - Индекс всей документации
- `.apply_migration.sh` - Скрипт автоматического применения миграций

## Применение миграций

### Быстрый способ: Автоматический скрипт (Рекомендуется)

```bash
# Применить миграцию автоматически (использует DATABASE_URL из .env)
./migrations/.apply_migration.sh

# Или указать конкретный файл миграции
./migrations/.apply_migration.sh migrations/0001_init.sql
```

Скрипт автоматически:
- Проверит наличие .env файла и DATABASE_URL
- Применит миграцию
- Покажет результат (список таблиц)

### Метод 1: Через psql (интерактивный режим)

```bash
# Подключиться к базе данных
psql -U username -d database_name

# Выполнить миграцию
\i /path/to/migrations/0001_init.sql

# Проверить результат
\dt
```

### Метод 2: Через psql (командная строка)

```bash
psql -U username -d database_name -f migrations/0001_init.sql
```

### Метод 3: Через переменные окружения

```bash
# Используя DATABASE_URL из .env
export DATABASE_URL="postgresql://user:password@localhost:5432/bot_db"

# Извлечь параметры подключения и выполнить миграцию
psql $DATABASE_URL -f migrations/0001_init.sql
```

### Метод 4: Через Docker (если база данных в контейнере)

```bash
docker exec -i postgres_container psql -U username -d database_name < migrations/0001_init.sql
```

## Проверка применения миграций

После применения миграции проверьте результат:

```sql
-- Список всех таблиц
\dt

-- Описание конкретной таблицы с индексами
\d bot_users
\d readings
\d steps
\d questions
\d payments

-- Проверка внешних ключей
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- Проверка индексов
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

## Структура таблиц

### bot_users
Пользователи Telegram бота
- **Первичный ключ:** id
- **Уникальные поля:** telegram_id
- **Индексы:** telegram_id, username, created_at

### readings
Записи чтений/сессий пользователей
- **Первичный ключ:** id
- **Внешние ключи:** user_id → bot_users.id (CASCADE)
- **Индексы:** user_id, status, created_at, reading_type, reading_payload (GIN)

### steps
Шаги в процессе (онбординг, обучение, опросы)
- **Первичный ключ:** id
- **Уникальные поля:** step_order
- **Индексы:** step_order, is_active

### questions
Вопросы для шагов процесса
- **Первичный ключ:** id
- **Внешние ключи:** step_id → steps.id (CASCADE)
- **Индексы:** step_id, (step_id, question_order), options (GIN)
- **Уникальные ограничения:** (step_id, question_order)

### payments
Платежи пользователей через Yookassa
- **Первичный ключ:** id
- **Внешние ключи:** user_id → bot_users.id (CASCADE)
- **Уникальные поля:** yookassa_payment_id
- **Индексы:** user_id, status, created_at, yookassa_payment_id, metadata (GIN)

## Каскадные правила

- **bot_users → readings**: ON DELETE CASCADE - удаление пользователя удаляет все его чтения
- **bot_users → payments**: ON DELETE CASCADE - удаление пользователя удаляет все его платежи
- **steps → questions**: ON DELETE CASCADE - удаление шага удаляет все связанные вопросы

## Триггеры

Автоматическое обновление поля `updated_at` при изменении записей в таблицах:
- bot_users
- steps
- questions
- payments

## Откат миграции

Если необходимо откатить миграцию:

```sql
-- ВНИМАНИЕ: Это удалит все данные!
BEGIN;

DROP TRIGGER IF EXISTS trigger_payments_updated_at ON payments;
DROP TRIGGER IF EXISTS trigger_questions_updated_at ON questions;
DROP TRIGGER IF EXISTS trigger_steps_updated_at ON steps;
DROP TRIGGER IF EXISTS trigger_bot_users_updated_at ON bot_users;

DROP FUNCTION IF EXISTS update_updated_at_column();

DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS steps CASCADE;
DROP TABLE IF EXISTS readings CASCADE;
DROP TABLE IF EXISTS bot_users CASCADE;

COMMIT;
```

## Добавление новых миграций

При добавлении новых миграций следуйте соглашению об именовании:
- `0002_description.sql`
- `0003_description.sql`
- и т.д.

Каждая миграция должна:
1. Начинаться с `BEGIN;`
2. Заканчиваться `COMMIT;`
3. Включать комментарии на русском языке
4. Быть идемпотентной (использовать `IF NOT EXISTS` где возможно)
5. Иметь инструкции по применению в комментариях
