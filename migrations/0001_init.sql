-- =====================================================================================================================
-- МИГРАЦИЯ: 0001_init.sql
-- ОПИСАНИЕ: Инициализация базы данных для Telegram бота
-- СОЗДАНИЕ: Таблицы bot_users, readings, steps, questions, payments
-- =====================================================================================================================
--
-- ИНСТРУКЦИЯ ПО ПРИМЕНЕНИЮ:
--
-- 1. Подключитесь к базе данных PostgreSQL:
--    psql -U username -d database_name
--
-- 2. Выполните миграцию:
--    \i /path/to/migrations/0001_init.sql
--
--    ИЛИ через командную строку:
--    psql -U username -d database_name -f /path/to/migrations/0001_init.sql
--
-- 3. Проверьте результат:
--    \dt - список всех таблиц
--    \d table_name - описание конкретной таблицы с индексами и ограничениями
--
-- ПРИМЕЧАНИЯ:
-- - Все изменения выполняются в транзакции
-- - При ошибке все изменения будут откатаны
-- - Миграция идемпотентна (можно запускать несколько раз)
-- =====================================================================================================================

BEGIN;

-- =====================================================================================================================
-- ТАБЛИЦА: bot_users
-- ОПИСАНИЕ: Хранит информацию о пользователях Telegram бота
-- =====================================================================================================================

CREATE TABLE IF NOT EXISTS bot_users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    username VARCHAR(255),
    is_bot BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE bot_users IS 'Пользователи Telegram бота';
COMMENT ON COLUMN bot_users.id IS 'Первичный ключ';
COMMENT ON COLUMN bot_users.telegram_id IS 'Уникальный идентификатор пользователя в Telegram';
COMMENT ON COLUMN bot_users.first_name IS 'Имя пользователя';
COMMENT ON COLUMN bot_users.last_name IS 'Фамилия пользователя';
COMMENT ON COLUMN bot_users.username IS 'Username в Telegram (без @)';
COMMENT ON COLUMN bot_users.is_bot IS 'Флаг: является ли пользователь ботом';
COMMENT ON COLUMN bot_users.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN bot_users.updated_at IS 'Дата и время последнего обновления записи';

-- Индексы для оптимизации поиска
CREATE INDEX IF NOT EXISTS idx_bot_users_telegram_id ON bot_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_bot_users_username ON bot_users(username) WHERE username IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_bot_users_created_at ON bot_users(created_at);

-- =====================================================================================================================
-- ТАБЛИЦА: readings
-- ОПИСАНИЕ: Хранит записи чтений/сессий пользователей
-- =====================================================================================================================

CREATE TABLE IF NOT EXISTS readings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES bot_users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    reading_type VARCHAR(100) NOT NULL,
    reading_payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE readings IS 'Записи чтений/сессий пользователей';
COMMENT ON COLUMN readings.id IS 'Первичный ключ';
COMMENT ON COLUMN readings.user_id IS 'Внешний ключ на пользователя';
COMMENT ON COLUMN readings.reading_type IS 'Тип чтения (например: tarot, astrology, numerology)';
COMMENT ON COLUMN readings.reading_payload IS 'Данные чтения в формате JSON';
COMMENT ON COLUMN readings.status IS 'Статус чтения (pending, in_progress, completed, cancelled)';
COMMENT ON COLUMN readings.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN readings.completed_at IS 'Дата и время завершения чтения';

-- Индексы для оптимизации поиска
CREATE INDEX IF NOT EXISTS idx_readings_user_id ON readings(user_id);
CREATE INDEX IF NOT EXISTS idx_readings_status ON readings(status);
CREATE INDEX IF NOT EXISTS idx_readings_created_at ON readings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_readings_reading_type ON readings(reading_type);
-- GIN индекс для эффективного поиска по JSONB полям
CREATE INDEX IF NOT EXISTS idx_readings_payload_gin ON readings USING GIN(reading_payload);

-- =====================================================================================================================
-- ТАБЛИЦА: steps
-- ОПИСАНИЕ: Хранит информацию о шагах в процессе (онбординг, обучение, опросы и т.д.)
-- =====================================================================================================================

CREATE TABLE IF NOT EXISTS steps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    step_order INTEGER NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE steps IS 'Шаги в процессе (онбординг, обучение, опросы)';
COMMENT ON COLUMN steps.id IS 'Первичный ключ';
COMMENT ON COLUMN steps.name IS 'Название шага';
COMMENT ON COLUMN steps.description IS 'Описание шага';
COMMENT ON COLUMN steps.step_order IS 'Порядковый номер шага (уникальный)';
COMMENT ON COLUMN steps.is_active IS 'Флаг активности шага';
COMMENT ON COLUMN steps.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN steps.updated_at IS 'Дата и время последнего обновления записи';

-- Индексы для оптимизации поиска
CREATE INDEX IF NOT EXISTS idx_steps_order ON steps(step_order);
CREATE INDEX IF NOT EXISTS idx_steps_active ON steps(is_active) WHERE is_active = TRUE;

-- =====================================================================================================================
-- ТАБЛИЦА: questions
-- ОПИСАНИЕ: Хранит вопросы, связанные с шагами процесса
-- =====================================================================================================================

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    step_id INTEGER NOT NULL REFERENCES steps(id) ON DELETE CASCADE ON UPDATE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL DEFAULT 'text',
    options JSONB DEFAULT '[]'::JSONB,
    question_order INTEGER NOT NULL,
    is_required BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE questions IS 'Вопросы для шагов процесса';
COMMENT ON COLUMN questions.id IS 'Первичный ключ';
COMMENT ON COLUMN questions.step_id IS 'Внешний ключ на шаг (удаление шага удаляет вопросы)';
COMMENT ON COLUMN questions.question_text IS 'Текст вопроса';
COMMENT ON COLUMN questions.question_type IS 'Тип вопроса (text, choice, multiple_choice, rating, date)';
COMMENT ON COLUMN questions.options IS 'Варианты ответов для вопросов с выбором (JSON массив)';
COMMENT ON COLUMN questions.question_order IS 'Порядковый номер вопроса внутри шага';
COMMENT ON COLUMN questions.is_required IS 'Обязателен ли ответ на вопрос';
COMMENT ON COLUMN questions.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN questions.updated_at IS 'Дата и время последнего обновления записи';

-- Индексы для оптимизации поиска
CREATE INDEX IF NOT EXISTS idx_questions_step_id ON questions(step_id);
CREATE INDEX IF NOT EXISTS idx_questions_order ON questions(step_id, question_order);
-- GIN индекс для эффективного поиска по JSONB полям
CREATE INDEX IF NOT EXISTS idx_questions_options_gin ON questions USING GIN(options);

-- Уникальное ограничение: в рамках одного шага не может быть вопросов с одинаковым порядковым номером
CREATE UNIQUE INDEX IF NOT EXISTS idx_questions_step_order_unique ON questions(step_id, question_order);

-- =====================================================================================================================
-- ТАБЛИЦА: payments
-- ОПИСАНИЕ: Хранит информацию о платежах через Yookassa
-- =====================================================================================================================

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES bot_users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    yookassa_payment_id VARCHAR(255) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'RUB' NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    description TEXT,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE payments IS 'Платежи пользователей через Yookassa';
COMMENT ON COLUMN payments.id IS 'Первичный ключ';
COMMENT ON COLUMN payments.user_id IS 'Внешний ключ на пользователя';
COMMENT ON COLUMN payments.yookassa_payment_id IS 'Уникальный идентификатор платежа в системе Yookassa';
COMMENT ON COLUMN payments.amount IS 'Сумма платежа (должна быть больше 0)';
COMMENT ON COLUMN payments.currency IS 'Валюта платежа (ISO 4217, например RUB, USD, EUR)';
COMMENT ON COLUMN payments.status IS 'Статус платежа (pending, processing, succeeded, cancelled, failed)';
COMMENT ON COLUMN payments.description IS 'Описание платежа для пользователя';
COMMENT ON COLUMN payments.metadata IS 'Дополнительные данные о платеже в формате JSON';
COMMENT ON COLUMN payments.created_at IS 'Дата и время создания платежа';
COMMENT ON COLUMN payments.updated_at IS 'Дата и время последнего обновления статуса платежа';

-- Индексы для оптимизации поиска
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_yookassa_id ON payments(yookassa_payment_id) WHERE yookassa_payment_id IS NOT NULL;
-- GIN индекс для эффективного поиска по JSONB полям
CREATE INDEX IF NOT EXISTS idx_payments_metadata_gin ON payments USING GIN(metadata);

-- =====================================================================================================================
-- ТРИГГЕРЫ: Автоматическое обновление поля updated_at
-- =====================================================================================================================

-- Функция для обновления поля updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS 'Автоматически обновляет поле updated_at при изменении записи';

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER trigger_bot_users_updated_at
    BEFORE UPDATE ON bot_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_steps_updated_at
    BEFORE UPDATE ON steps
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_questions_updated_at
    BEFORE UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================================================================
-- ЗАВЕРШЕНИЕ МИГРАЦИИ
-- =====================================================================================================================

COMMIT;

-- =====================================================================================================================
-- ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ (ЗАКОММЕНТИРОВАНЫ)
-- =====================================================================================================================

/*
-- Создание пользователя
INSERT INTO bot_users (telegram_id, first_name, last_name, username)
VALUES (123456789, 'Иван', 'Петров', 'ivan_petrov');

-- Создание шага
INSERT INTO steps (name, description, step_order)
VALUES ('Приветствие', 'Первый шаг - приветствие пользователя', 1);

-- Создание вопроса для шага
INSERT INTO questions (step_id, question_text, question_type, options, question_order)
VALUES (1, 'Как вас зовут?', 'text', '[]'::JSONB, 1);

-- Создание чтения для пользователя
INSERT INTO readings (user_id, reading_type, reading_payload, status)
VALUES (1, 'tarot', '{"cards": ["The Fool", "The Magician"]}'::JSONB, 'completed');

-- Создание платежа
INSERT INTO payments (user_id, yookassa_payment_id, amount, currency, status, description)
VALUES (1, 'yookassa_12345', 499.00, 'RUB', 'succeeded', 'Оплата консультации');

-- Выборка всех активных шагов с вопросами
SELECT s.*, q.question_text, q.question_order
FROM steps s
LEFT JOIN questions q ON s.id = q.step_id
WHERE s.is_active = TRUE
ORDER BY s.step_order, q.question_order;

-- Выборка всех платежей пользователя
SELECT p.*, u.first_name, u.last_name
FROM payments p
JOIN bot_users u ON p.user_id = u.id
WHERE u.telegram_id = 123456789
ORDER BY p.created_at DESC;
*/
