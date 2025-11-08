"""Пример сервиса с использованием репозиториев."""

import logging
from typing import Optional, List

from ..models.user import UserCreate
from ..models.reading import ReadingCreate
from ..models.payment import PaymentCreate
from ..models.step import StepCreate
from ..models.question import QuestionCreate
from .user_repository import UserRepository
from .reading_repository import ReadingRepository
from .payment_repository import PaymentRepository
from .step_repository import StepRepository
from .question_repository import QuestionRepository

logger = logging.getLogger(__name__)


class ExampleService:
    """Пример класса сервиса для бизнес-логики с использованием репозиториев."""

    @staticmethod
    async def get_data() -> dict:
        """Пример метода для получения данных."""
        logger.info("Получение данных из сервиса")
        return {"status": "ok", "data": "Пример данных"}

    @staticmethod
    async def process_data(data: dict) -> dict:
        """Пример метода для обработки данных."""
        logger.info(f"Обработка данных: {data}")
        return {"status": "processed", "data": data}

    @staticmethod
    async def create_user_example(telegram_id: int, first_name: str, username: Optional[str] = None) -> UserCreate:
        """Пример создания пользователя через репозиторий."""
        try:
            user_data = UserCreate(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username
            )
            
            user = await UserRepository.create(user_data)
            logger.info(f"Пример: создан пользователь {user.first_name} (ID: {user.id})")
            return user
            
        except Exception as e:
            logger.error(f"Ошибка в примере создания пользователя: {str(e)}")
            raise

    @staticmethod
    async def get_user_balance(telegram_id: int) -> float:
        """Пример получения баланса пользователя через репозитории."""
        try:
            # Находим пользователя
            user = await UserRepository.get_by_telegram_id(telegram_id)
            if not user:
                raise ValueError(f"Пользователь с telegram_id {telegram_id} не найден")
            
            # Получаем общую сумму успешных платежей
            total_spent = await PaymentRepository.get_user_total_spent(user.id)
            
            # Здесь может быть логика расчета баланса
            # Например, баланс = сумма платежей - стоимость использованных услуг
            balance = float(total_spent)
            
            logger.info(f"Баланс пользователя {user.first_name}: {balance}")
            return balance
            
        except Exception as e:
            logger.error(f"Ошибка при получении баланса пользователя: {str(e)}")
            raise

    @staticmethod
    async def create_reading_example(user_id: int, reading_type: str, payload: dict) -> ReadingCreate:
        """Пример создания чтения через репозиторий."""
        try:
            reading_data = ReadingCreate(
                user_id=user_id,
                reading_type=reading_type,
                reading_payload=payload
            )
            
            reading = await ReadingRepository.create(reading_data)
            logger.info(f"Пример: создано чтение типа {reading_type} для пользователя {user_id}")
            return reading
            
        except Exception as e:
            logger.error(f"Ошибка в примере создания чтения: {str(e)}")
            raise

    @staticmethod
    async def get_active_steps_with_questions() -> List:
        """Пример получения активных шагов с вопросами."""
        try:
            steps_with_questions = await StepRepository.get_active_with_questions()
            logger.info(f"Получено {len(steps_with_questions)} активных шагов с вопросами")
            return steps_with_questions
            
        except Exception as e:
            logger.error(f"Ошибка при получении шагов с вопросами: {str(e)}")
            raise

    @staticmethod
    async def create_payment_example(user_id: int, amount: float, description: str) -> PaymentCreate:
        """Пример создания платежа через репозиторий."""
        try:
            from decimal import Decimal
            
            payment_data = PaymentCreate(
                user_id=user_id,
                amount=Decimal(str(amount)),
                description=description,
                status="pending"
            )
            
            payment = await PaymentRepository.create(payment_data)
            logger.info(f"Пример: создан платеж на сумму {amount} для пользователя {user_id}")
            return payment
            
        except Exception as e:
            logger.error(f"Ошибка в примере создания платежа: {str(e)}")
            raise

    @staticmethod
    async def complete_payment_example(payment_id: int, yookassa_payment_id: str) -> Optional:
        """Пример завершения платежа через репозиторий."""
        try:
            payment = await PaymentRepository.update_status(
                payment_id, 
                "succeeded", 
                yookassa_payment_id
            )
            
            if payment:
                logger.info(f"Пример: платеж {payment_id} успешно завершен")
            else:
                logger.warning(f"Пример: платеж {payment_id} не найден")
            
            return payment
            
        except Exception as e:
            logger.error(f"Ошибка в примере завершения платежа: {str(e)}")
            raise
