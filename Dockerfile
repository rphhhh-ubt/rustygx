# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY src/ ./src/
COPY migrations/ ./migrations/

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Устанавливаем переменные окружения по умолчанию
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Запускаем приложение
CMD ["python", "-m", "src.main"]