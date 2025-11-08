#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы слоя базы данных.
Запускать после настройки .env файла с DATABASE_URL.
"""

import asyncio
import logging
import os
from decimal import Decimal
from pathlib import Path

# Добавляем src в Python path
src_path = Path(__file__).parent / "src"
import sys
sys.path.insert(0, str(src_path))

from src.services import (
    init_database, close_database, test_connection,
    UserRepository, ReadingRepository, PaymentRepository,
    StepRepository, QuestionRepository
)
from src.models import (
    UserCreate, ReadingCreate, PaymentCreate, 
    StepCreate, QuestionCreate
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_user_repository():
    """Тестирование репозитория пользователей."""
    logger.info("=== Тестирование UserRepository ===")
    
    try:
        # Создание пользователя
        user_data = UserCreate(
            telegram_id=123456789,
            first_name="Тестовый",
            last_name="Пользователь",
            username="test_user"
        )
        
        user = await UserRepository.create(user_data)
        logger.info(f"Создан пользователь: {user}")
        
        # Получение пользователя по telegram_id
        found_user = await UserRepository.get_by_telegram_id(123456789)
        logger.info(f"Найден пользователь: {found_user}")
        
        # Получение или создание (get_or_create)
        existing_user = await UserRepository.get_or_create(123456789, user_data)
        logger.info(f"Существующий пользователь: {existing_user}")
        
        return user.id
        
    except Exception as e:
        logger.error(f"Ошибка в UserRepository: {str(e)}")
        raise


async def test_step_repository():
    """Тестирование репозитория шагов."""
    logger.info("=== Тестирование StepRepository ===")
    
    try:
        # Создание шага
        step_data = StepCreate(
            name="Тестовый шаг",
            description="Описание тестового шага",
            step_order=1,
            is_active=True
        )
        
        step = await StepRepository.create(step_data)
        logger.info(f"Создан шаг: {step}")
        
        # Создание вопроса для шага
        question_data = QuestionCreate(
            step_id=step.id,
            question_text="Как ваше настроение?",
            question_type="text",
            question_order=1,
            is_required=True
        )
        
        question = await QuestionRepository.create(question_data)
        logger.info(f"Создан вопрос: {question}")
        
        # Получение активных шагов с вопросами
        steps_with_questions = await StepRepository.get_active_with_questions()
        logger.info(f"Активные шаги с вопросами: {len(steps_with_questions)}")
        for step_with_q in steps_with_questions:
            logger.info(f"Шаг: {step_with_q.name}, вопросов: {len(step_with_q.questions)}")
        
        return step.id
        
    except Exception as e:
        logger.error(f"Ошибка в StepRepository: {str(e)}")
        raise


async def test_reading_repository(user_id: int):
    """Тестирование репозитория чтений."""
    logger.info("=== Тестирование ReadingRepository ===")
    
    try:
        # Создание чтения
        reading_data = ReadingCreate(
            user_id=user_id,
            reading_type="tarot",
            reading_payload={"cards": ["The Fool", "The Magician"], "question": "Что меня ждет?"},
            status="pending"
        )
        
        reading = await ReadingRepository.create(reading_data)
        logger.info(f"Создано чтение: {reading}")
        
        # Завершение чтения
        completed_reading = await ReadingRepository.complete_reading(reading.id)
        logger.info(f"Завершенное чтение: {completed_reading}")
        
        # Получение чтений пользователя
        user_readings = await ReadingRepository.get_by_user_id(user_id)
        logger.info(f"Чтения пользователя: {len(user_readings)}")
        
        return reading.id
        
    except Exception as e:
        logger.error(f"Ошибка в ReadingRepository: {str(e)}")
        raise


async def test_payment_repository(user_id: int):
    """Тестирование репозитория платежей."""
    logger.info("=== Тестирование PaymentRepository ===")
    
    try:
        # Создание платежа
        payment_data = PaymentCreate(
            user_id=user_id,
            amount=Decimal("499.99"),
            currency="RUB",
            description="Оплата консультации",
            status="pending"
        )
        
        payment = await PaymentRepository.create(payment_data)
        logger.info(f"Создан платеж: {payment}")
        
        # Обновление статуса платежа
        updated_payment = await PaymentRepository.update_status(
            payment.id, 
            "succeeded", 
            "yookassa_test_12345"
        )
        logger.info(f"Обновленный платеж: {updated_payment}")
        
        # Получение баланса пользователя
        total_spent = await PaymentRepository.get_user_total_spent(user_id)
        logger.info(f"Общая сумма потраченных средств: {total_spent}")
        
        return payment.id
        
    except Exception as e:
        logger.error(f"Ошибка в PaymentRepository: {str(e)}")
        raise


async def main():
    """Основная функция тестирования."""
    logger.info("Начало тестирования слоя базы данных...")
    
    try:
        # Проверка наличия DATABASE_URL
        if not os.getenv("DATABASE_URL"):
            logger.error("DATABASE_URL не найден. Установите переменную окружения или создайте .env файл.")
            return
        
        # Инициализация базы данных
        await init_database()
        
        # Тестирование соединения
        connection_ok = await test_connection()
        if not connection_ok:
            logger.error("Не удалось установить соединение с базой данных")
            return
        
        logger.info("Соединение с базой данных установлено успешно!")
        
        # Тестирование репозиториев
        user_id = await test_user_repository()
        step_id = await test_step_repository()
        reading_id = await test_reading_repository(user_id)
        payment_id = await test_payment_repository(user_id)
        
        logger.info("=== Все тесты успешно пройдены! ===")
        logger.info(f"Созданные сущности: user_id={user_id}, step_id={step_id}, reading_id={reading_id}, payment_id={payment_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {str(e)}")
    finally:
        # Закрытие соединений
        await close_database()
        logger.info("Тестирование завершено")


if __name__ == "__main__":
    asyncio.run(main())