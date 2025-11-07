-- Миграция 0001: Инициализация базы данных
-- 
-- Порядок применения:
-- 1. Убедитесь, что база данных создана
-- 2. Примените миграцию через psql: psql -d your_database -f migrations/0001_init.sql
-- 3. Или используйте миграционный инструмент вроде migrate: migrate -path migrations -database "postgres://..." up
--
-- Таблицы создаются в порядке зависимостей для соблюдения внешних ключей

-- Таблица пользователей бота
CREATE TABLE bot_users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице bot_users
COMMENT ON TABLE bot_users IS 'Пользователи бота';
COMMENT ON COLUMN bot_users.id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN bot_users.telegram_id IS 'ID пользователя в Telegram';
COMMENT ON COLUMN bot_users.username IS 'Имя пользователя в Telegram';
COMMENT ON COLUMN bot_users.first_name IS 'Имя пользователя';
COMMENT ON COLUMN bot_users.last_name IS 'Фамилия пользователя';
COMMENT ON COLUMN bot_users.is_active IS 'Флаг активности пользователя';
COMMENT ON COLUMN bot_users.created_at IS 'Время создания записи';
COMMENT ON COLUMN bot_users.updated_at IS 'Время последнего обновления записи';

-- Таблица показаний/измерений
CREATE TABLE readings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES bot_users(id) ON DELETE CASCADE,
    payload JSONB NOT NULL,
    reading_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице readings
COMMENT ON TABLE readings IS 'Показания/измерения пользователей';
COMMENT ON COLUMN readings.id IS 'Уникальный идентификатор показания';
COMMENT ON COLUMN readings.user_id IS 'ID пользователя';
COMMENT ON COLUMN readings.payload IS 'Данные показания в формате JSON';
COMMENT ON COLUMN readings.reading_date IS 'Дата показания';
COMMENT ON COLUMN readings.created_at IS 'Время создания записи';
COMMENT ON COLUMN readings.updated_at IS 'Время последнего обновления записи';

-- Таблица шагов
CREATE TABLE steps (
    id SERIAL PRIMARY KEY,
    step_order INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице steps
COMMENT ON TABLE steps IS 'Шаги процесса';
COMMENT ON COLUMN steps.id IS 'Уникальный идентификатор шага';
COMMENT ON COLUMN steps.step_order IS 'Порядковый номер шага';
COMMENT ON COLUMN steps.title IS 'Заголовок шага';
COMMENT ON COLUMN steps.description IS 'Описание шага';
COMMENT ON COLUMN steps.is_active IS 'Флаг активности шага';
COMMENT ON COLUMN steps.created_at IS 'Время создания записи';
COMMENT ON COLUMN steps.updated_at IS 'Время последнего обновления записи';

-- Таблица вопросов
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    step_id INTEGER NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL, -- 'text', 'number', 'choice', etc.
    is_required BOOLEAN DEFAULT true,
    order_in_step INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Уникальное ограничение: один вопрос не может повторяться в одном шаге
    UNIQUE(step_id, question_text)
);

-- Комментарии к таблице questions
COMMENT ON TABLE questions IS 'Вопросы для шагов';
COMMENT ON COLUMN questions.id IS 'Уникальный идентификатор вопроса';
COMMENT ON COLUMN questions.step_id IS 'ID шага';
COMMENT ON COLUMN questions.question_text IS 'Текст вопроса';
COMMENT ON COLUMN questions.question_type IS 'Тип вопроса';
COMMENT ON COLUMN questions.is_required IS 'Обязательность ответа';
COMMENT ON COLUMN questions.order_in_step IS 'Порядковый номер вопроса в шаге';
COMMENT ON COLUMN questions.created_at IS 'Время создания записи';
COMMENT ON COLUMN questions.updated_at IS 'Время последнего обновления записи';

-- Таблица платежей
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES bot_users(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RUB',
    payment_method VARCHAR(50) NOT NULL, -- 'card', 'cash', etc.
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'cancelled'
    payment_date TIMESTAMP WITH TIME ZONE,
    external_payment_id VARCHAR(255), -- ID внешней платежной системы
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице payments
COMMENT ON TABLE payments IS 'Платежи пользователей';
COMMENT ON COLUMN payments.id IS 'Уникальный идентификатор платежа';
COMMENT ON COLUMN payments.user_id IS 'ID пользователя';
COMMENT ON COLUMN payments.amount IS 'Сумма платежа';
COMMENT ON COLUMN payments.currency IS 'Валюта платежа';
COMMENT ON COLUMN payments.payment_method IS 'Способ оплаты';
COMMENT ON COLUMN payments.status IS 'Статус платежа';
COMMENT ON COLUMN payments.payment_date IS 'Дата совершения платежа';
COMMENT ON COLUMN payments.external_payment_id IS 'ID во внешней платежной системе';
COMMENT ON COLUMN payments.description IS 'Описание платежа';
COMMENT ON COLUMN payments.created_at IS 'Время создания записи';
COMMENT ON COLUMN payments.updated_at IS 'Время последнего обновления записи';

-- Индексы для оптимизации выборок

-- Индексы для bot_users
CREATE INDEX idx_bot_users_telegram_id ON bot_users(telegram_id);
CREATE INDEX idx_bot_users_is_active ON bot_users(is_active);

-- Индексы для readings
CREATE INDEX idx_readings_user_id ON readings(user_id);
CREATE INDEX idx_readings_reading_date ON readings(reading_date);
CREATE INDEX idx_readings_payload ON readings USING GIN(payload); -- GIN индекс для JSONB

-- Индексы для steps
CREATE INDEX idx_steps_step_order ON steps(step_order);
CREATE INDEX idx_steps_is_active ON steps(is_active);

-- Индексы для questions
CREATE INDEX idx_questions_step_id ON questions(step_id);
CREATE INDEX idx_questions_order_in_step ON questions(step_id, order_in_step);
CREATE INDEX idx_questions_question_type ON questions(question_type);

-- Индексы для payments
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_payment_date ON payments(payment_date);
CREATE INDEX idx_payments_external_payment_id ON payments(external_payment_id) WHERE external_payment_id IS NOT NULL;

-- Триггеры для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Применение триггера ко всем таблицам с полем updated_at
CREATE TRIGGER update_bot_users_updated_at BEFORE UPDATE ON bot_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_readings_updated_at BEFORE UPDATE ON readings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_steps_updated_at BEFORE UPDATE ON steps FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON questions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Добавляем ограничения CHECK для валидации данных
ALTER TABLE payments ADD CONSTRAINT check_amount_positive CHECK (amount > 0);
ALTER TABLE payments ADD CONSTRAINT check_currency_format CHECK (currency ~ '^[A-Z]{3}$');
ALTER TABLE payments ADD CONSTRAINT check_status_valid CHECK (status IN ('pending', 'completed', 'failed', 'cancelled'));
ALTER TABLE questions ADD CONSTRAINT check_order_positive CHECK (order_in_step > 0);
ALTER TABLE steps ADD CONSTRAINT check_step_order_positive CHECK (step_order > 0);
