"""Обработчики основных команд бота."""

import logging
from aiogram import Router, types
from aiogram.filters import Command

from src.locales import messages

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """Обработчик команды /start."""
    logger.info(f"Пользователь {message.from_user.id} запустил /start")
    await message.answer(messages.START_MESSAGE)


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
