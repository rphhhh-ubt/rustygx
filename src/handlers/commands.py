"""Обработчики основных команд бота."""

import logging
from typing import Optional
from aiogram import Router, types, Bot
from aiogram.filters import Command

from src.locales import messages
from src.services.user_repository import UserRepository
from src.services.reading_repository import ReadingRepository
from src.services.scenario_service import ScenarioService
from src.models.user import UserCreate
from src.config import settings

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot) -> None:
    """Обработчик команды /start."""
    try:
        user_telegram_id = message.from_user.id
        logger.info(f"Пользователь {user_telegram_id} запустил /start")
        
        # Проверяем наличие пользователя в БД
        user = await UserRepository.get_by_telegram_id(user_telegram_id)
        
        if user is None:
            # Создаем нового пользователя
            user_data = UserCreate(
                telegram_id=user_telegram_id,
                first_name=message.from_user.first_name or "Пользователь",
                last_name=message.from_user.last_name,
                username=message.from_user.username,
                is_bot=message.from_user.is_bot
            )
            user = await UserRepository.create(user_data)
            welcome_msg = messages.START_USER_CREATED.format(first_name=user.first_name)
            logger.info(f"Создан новый пользователь {user.id} ({user_telegram_id})")
        else:
            welcome_msg = messages.START_USER_EXISTS.format(first_name=user.first_name)
            logger.info(f"Пользователь {user.id} ({user_telegram_id}) уже существует")
        
        # Получаем баланс пользователя
        scenario_service = ScenarioService(bot)
        balance = await scenario_service.get_user_balance(user.id)
        
        # Формируем сообщение с приветствием и балансом
        balance_msg = messages.USER_BALANCE.format(
            free_readings=balance["free_readings"],
            paid_readings=balance["paid_readings"]
        )
        
        full_message = f"{welcome_msg}\n\n{balance_msg}"
        await message.answer(full_message)
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {str(e)}")
        await message.answer(messages.ERROR_MESSAGE)


@router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    """Обработчик команды /help."""
    logger.info(f"Пользователь {message.from_user.id} запросил /help")
    await message.answer(messages.HELP_MESSAGE)


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message) -> None:
    """Обработчик команды /cancel."""
    logger.info(f"Пользователь {message.from_user.id} отменил операцию")
    await message.answer(messages.CANCEL_MESSAGE)
