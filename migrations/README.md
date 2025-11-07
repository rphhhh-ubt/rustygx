# Database Migrations

This directory contains SQL migration files for the database schema.

## Migration Files

### 0001_init.sql
Initial database schema migration that creates the following tables:

- **bot_users** - Пользователи бота с интеграцией Telegram
- **readings** - Показания/измерения пользователей в формате JSONB
- **steps** - Шаги процесса с порядковой нумерацией
- **questions** - Вопросы, привязанные к шагам
- **payments** - Информация о платежах с отслеживанием статусов

## Применение миграций

### Способ 1: Использование psql
```bash
psql -d your_database -f migrations/0001_init.sql
```

### Способ 2: Использование migrate
```bash
migrate -path migrations -database "postgres://username:password@localhost/database?sslmode=disable" up
```

## Особенности схемы

- **Каскадное удаление**: Удаление пользователя удаляет все связанные записи
- **Автоматические временные метки**: Триггеры автоматически обновляют `updated_at`
- **Оптимизированные индексы**: Созданы индексы для часто используемых полей
- **Валидация данных**: CHECK ограничения для обеспечения целостности данных
- **Поддержка JSONB**: Эффективное хранение структурированных данных в таблице readings

## Порядок применения

Миграции должны применяться в порядке номерации (0001, 0002, и т.д.) для соблюдения зависимостей.
