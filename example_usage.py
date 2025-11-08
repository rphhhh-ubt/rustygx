#!/usr/bin/env python3
"""
Пример использования слоя базы данных в Telegram боте.
Показывает интеграцию с обработчиками сообщений.
"""

import asyncio
import logging
from pathlib import Path
from decimal import Decimal

# Добавляем src в Python path
src_path = Path(__file__).parent / "src"
import sys
sys.path.insert(0, str(src_path))

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from src.config import settings
from src.services import init_database, close_database
from src.services import UserRepository, PaymentRepository, ReadingRepository, StepRepository
from src.models import UserCreate, ReadingCreate, PaymentCreate

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.bot_token)
dp = Dispatcher()


@dp.message(Command("start"))
async def handle_start(message: types.Message) -> None:
    """Обработчик команды /start с созданием пользователя."""
    try:
        # Создаем или получаем пользователя
        user_data = UserCreate(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username
        )
        
        user = await UserRepository.get_or_create(
            message.from_user.id, 
            user_data
        )
        
        await message.answer(
            f"👋 Привет, {user.first_name}! "
            f"Ваш ID в системе: {user.id}\n"
            f"Telegram ID: {user.telegram_id}"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {str(e)}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@dp.message(Command("balance"))
async def handle_balance(message: types.Message) -> None:
    """Обработчик команды /balance для получения баланса."""
    try:
        # Получаем пользователя
        user = await UserRepository.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        # Получаем общую сумму потраченных средств
        total_spent = await PaymentRepository.get_user_total_spent(user.id)
        
        await message.answer(
            f"💳 Ваш баланс:\n"
            f"Потрачено: {total_spent} ₽\n"
            f"Количество платежей: {await PaymentRepository.get_user_payment_count(user.id)}"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /balance: {str(e)}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@dp.message(Command("reading"))
async def handle_reading(message: types.Message) -> None:
    """Обработчик команды /reading для создания чтения."""
    try:
        # Получаем пользователя
        user = await UserRepository.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        # Создаем новое чтение
        reading_data = ReadingCreate(
            user_id=user.id,
            reading_type="tarot",
            reading_payload={
                "question": "Что меня ждет в будущем?",
                "cards": ["The Fool", "The Magician"]
            },
            status="pending"
        )
        
        reading = await ReadingRepository.create(reading_data)
        
        await message.answer(
            f"🔮 Создано новое чтение:\n"
            f"ID: {reading.id}\n"
            f"Тип: {reading.reading_type}\n"
            f"Статус: {reading.status}\n"
            f"Вопрос: {reading.reading_payload.get('question', 'Без вопроса')}"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /reading: {str(e)}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@dp.message(Command("payment"))
async def handle_payment(message: types.Message) -> None:
    """Обработчик команды /payment для создания платежа."""
    try:
        # Получаем пользователя
        user = await UserRepository.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        # Создаем платеж
        payment_data = PaymentCreate(
            user_id=user.id,
            amount=Decimal("299.99"),
            description="Оплата Таро консультации",
            status="pending"
        )
        
        payment = await PaymentRepository.create(payment_data)
        
        await message.answer(
            f"💳 Создан платеж:\n"
            f"ID: {payment.id}\n"
            f"Сумма: {payment.amount} {payment.currency}\n"
            f"Описание: {payment.description}\n"
            f"Статус: {payment.status}\n\n"
            f"Для завершения оплаты используйте команду /pay_{payment.id}"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /payment: {str(e)}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@dp.message(Command("steps"))
async def handle_steps(message: types.Message) -> None:
    """Обработчик команды /steps для получения шагов."""
    try:
        # Получаем активные шаги с вопросами
        steps_with_questions = await StepRepository.get_active_with_questions()
        
        if not steps_with_questions:
            await message.answer("📋 Активных шагов не найдено")
            return
        
        response_text = "📋 Активные шаги:\n\n"
        
        for step in steps_with_questions:
            response_text += f"🔹 {step.step_order}. {step.name}\n"
            if step.description:
                response_text += f"   {step.description}\n"
            
            if step.questions:
                response_text += "   Вопросы:\n"
                for question in step.questions:
                    required_text = " (обязательный)" if question.is_required else ""
                    response_text += f"   • {question.question_order}. {question.question_text}{required_text}\n"
            
            response_text += "\n"
        
        await message.answer(response_text)
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /steps: {str(e)}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@dp.message(Command("my_readings"))
async def handle_my_readings(message: types.Message) -> None:
    """Обработчик команды /my_readings для получения чтений пользователя."""
    try:
        # Получаем пользователя
        user = await UserRepository.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        # Получаем чтения пользователя
        readings = await ReadingRepository.get_by_user_id(user.id, limit=10)
        
        if not readings:
            await message.answer("📖 У вас пока нет чтений")
            return
        
        response_text = f"📖 Ваши чтения ({len(readings)} последних):\n\n"
        
        for reading in readings:
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄", 
                "completed": "✅",
                "cancelled": "❌"
            }.get(reading.status, "❓")
            
            response_text += (
                f"{status_emoji} Чтение #{reading.id}\n"
                f"Тип: {reading.reading_type}\n"
                f"Статус: {reading.status}\n"
                f"Создано: {reading.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            )
            
            if reading.completed_at:
                response_text += f"Завершено: {reading.completed_at.strftime('%d.%m.%Y %H:%M')}\n"
            
            response_text += "\n"
        
        await message.answer(response_text)
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /my_readings: {str(e)}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


async def main() -> None:
    """Основная функция."""
    logger.info("Запуск примера использования слоя базы данных...")
    
    try:
        # Инициализация базы данных
        await init_database()
        logger.info("База данных инициализирована")
        
        # Запуск бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске: {str(e)}")
    finally:
        # Закрытие соединений
        await close_database()
        logger.info("Приложение остановлено")


if __name__ == "__main__":
    asyncio.run(main())