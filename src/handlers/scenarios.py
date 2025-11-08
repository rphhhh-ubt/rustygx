"""Обработчики сценариев и вопросов."""

import logging
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.types import Message

from src.locales import messages
from src.services.user_repository import UserRepository
from src.services.scenario_service import ScenarioService
from src.models.user import UserCreate

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("read"))
async def cmd_read(message: Message, bot: Bot, command: Command) -> None:
    """Обработчик команды /read с payload для запуска сценария.
    
    Использование:
    /read tarot - запуск сценария типа tarot
    /read default - запуск стандартного сценария
    """
    try:
        user_telegram_id = message.from_user.id
        payload = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        
        logger.info(f"Пользователь {user_telegram_id} запустил /read с payload={payload}")
        
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
            logger.info(f"Создан новый пользователь {user.id} ({user_telegram_id})")
        
        # Инициализируем сервис сценариев
        scenario_service = ScenarioService(bot)
        
        # Запускаем сценарий
        reading_id = await scenario_service.start_scenario(user.id, payload)
        
        if reading_id is None:
            await message.answer(messages.START_PAYLOAD_ERROR)
            return
        
        logger.info(f"Запущен сценарий {reading_id} для пользователя {user.id}")
        
        # Отправляем сообщение о начале сценария
        scenario_name = payload or "Стандартный сценарий"
        await message.answer(messages.SCENARIO_STARTED.format(scenario_name=scenario_name))
        
        # Проигрываем сценарий
        success = await scenario_service.play_scenario_steps(
            user.id,
            message.chat.id,
            reading_id
        )
        
        if not success:
            logger.error(f"Ошибка при проигрывании сценария {reading_id}")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /read: {str(e)}")
        await message.answer(messages.ERROR_MESSAGE)


@router.callback_query(F.data.startswith("answer_"))
async def answer_question(callback_query: types.CallbackQuery, bot: Bot) -> None:
    """Обработчик нажатия на кнопку ответа.
    
    Callback data формат: answer_<question_id>_<payload>
    """
    try:
        user_telegram_id = callback_query.from_user.id
        
        # Разбираем callback data
        parts = callback_query.data.split("_", 2)
        if len(parts) < 3:
            logger.warning(f"Неверный формат callback: {callback_query.data}")
            await callback_query.answer("❌ Ошибка при обработке ответа")
            return
        
        question_id = parts[1]
        payload = parts[2]
        
        logger.info(f"Пользователь {user_telegram_id} ответил на вопрос {question_id}: {payload}")
        
        # Отправляем подтверждение
        await callback_query.answer(f"✅ Ваш ответ: {payload}")
        
        # Если нужно сохранить ответ - добавить логику сохранения
        # Здесь можно обновить reading_payload с ответом
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике ответа: {str(e)}")
        await callback_query.answer("❌ Ошибка при обработке ответа")


@router.message(F.text == messages.BUTTON_SKIP)
async def skip_question(message: Message) -> None:
    """Обработчик нажатия на кнопку пропуска."""
    try:
        user_telegram_id = message.from_user.id
        logger.info(f"Пользователь {user_telegram_id} пропустил вопрос")
        
        await message.answer("⏭️ Вопрос пропущен")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике пропуска: {str(e)}")


@router.message(F.text == messages.BUTTON_YES)
async def answer_yes(message: Message) -> None:
    """Обработчик кнопки 'Да'."""
    try:
        user_telegram_id = message.from_user.id
        logger.info(f"Пользователь {user_telegram_id} ответил 'Да'")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике 'Да': {str(e)}")


@router.message(F.text == messages.BUTTON_NO)
async def answer_no(message: Message) -> None:
    """Обработчик кнопки 'Нет'."""
    try:
        user_telegram_id = message.from_user.id
        logger.info(f"Пользователь {user_telegram_id} ответил 'Нет'")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике 'Нет': {str(e)}")
