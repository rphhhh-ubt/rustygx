"""Обработчики администраторских команд."""

import logging
from aiogram import Router, types, F
from aiogram.filters import Command

from src.locales import messages
from src.config import settings

logger = logging.getLogger(__name__)

router = Router()


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором.
    
    Args:
        user_id: ID пользователя в Telegram
        
    Returns:
        True если админ, False иначе
    """
    return settings.admin_id > 0 and user_id == settings.admin_id


@router.message(Command("get_photo_id"))
async def cmd_get_photo_id(message: types.Message) -> None:
    """Обработчик команды /get_photo_id для получения file_id фото.
    
    Доступна только администраторам.
    Требует отправки фото после команды.
    """
    try:
        user_telegram_id = message.from_user.id
        
        # Проверяем, является ли пользователь админом
        if not is_admin(user_telegram_id):
            logger.warning(f"Попытка доступа к админ-команде от пользователя {user_telegram_id}")
            await message.answer(messages.ADMIN_ONLY)
            return
        
        logger.info(f"Администратор {user_telegram_id} запросил /get_photo_id")
        
        # Отправляем инструкцию
        await message.answer(messages.PHOTO_ID_INSTRUCTION)
        
        # Установим флаг ожидания фото в состояние (если используется FSM)
        # Здесь просто логируем
        logger.info("Ожидание фото от администратора")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /get_photo_id: {str(e)}")
        await message.answer(messages.ERROR_MESSAGE)


@router.message(F.photo, F.from_user.id == settings.admin_id)
async def handle_admin_photo(message: types.Message) -> None:
    """Обработчик фото для администратора (после команды /get_photo_id).
    
    Отправляет file_id загруженного фото.
    """
    try:
        user_telegram_id = message.from_user.id
        
        # Проверяем, является ли пользователь админом
        if not is_admin(user_telegram_id):
            logger.warning(f"Попытка отправки фото неадмином {user_telegram_id}")
            return
        
        # Получаем информацию о фото
        if message.photo:
            # Берем самое большое фото из массива
            photo = message.photo[-1]
            file_id = photo.file_id
            file_size = photo.file_size or 0
            
            logger.info(f"Администратор {user_telegram_id} отправил фото: {file_id}")
            
            # Отправляем file_id администратору
            response = messages.PHOTO_ID_RECEIVED.format(
                file_id=file_id,
                photo_type="large" if len(message.photo) > 1 else "small"
            )
            await message.answer(response)
            
            # Логируем информацию о фото
            logger.info(f"File ID: {file_id}, размер: {file_size} байт")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке фото админа: {str(e)}")
        await message.answer(messages.ERROR_MESSAGE)


@router.message(F.document)
async def handle_document(message: types.Message) -> None:
    """Обработчик документа - для администратора это ошибка."""
    try:
        user_telegram_id = message.from_user.id
        
        if is_admin(user_telegram_id):
            logger.warning(f"Администратор отправил документ вместо фото")
            await message.answer(messages.PHOTO_INVALID_TYPE)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке документа: {str(e)}")


@router.message(Command("stats"))
async def cmd_stats(message: types.Message) -> None:
    """Обработчик команды /stats для получения статистики (только для админов).
    
    Показывает:
    - Количество пользователей
    - Количество чтений
    - Статус базы данных
    """
    try:
        user_telegram_id = message.from_user.id
        
        # Проверяем, является ли пользователь админом
        if not is_admin(user_telegram_id):
            logger.warning(f"Попытка доступа к /stats от пользователя {user_telegram_id}")
            await message.answer(messages.ADMIN_ONLY)
            return
        
        logger.info(f"Администратор {user_telegram_id} запросил статистику")
        
        from src.services.user_repository import UserRepository
        from src.services.reading_repository import ReadingRepository
        
        try:
            # Получаем статистику
            all_users = await UserRepository.get_all(limit=1000)
            all_readings = await ReadingRepository.get_all(limit=1000)
            
            stats_text = f"""📊 Статистика бота:
👥 Всего пользователей: {len(all_users)}
📖 Всего чтений: {len(all_readings)}
✅ Завершенных: {len([r for r in all_readings if r.status == 'completed'])}
⏳ В процессе: {len([r for r in all_readings if r.status == 'in_progress'])}
⏸️ Отменено: {len([r for r in all_readings if r.status == 'cancelled'])}
            """
            
            await message.answer(stats_text)
            logger.info("Статистика отправлена администратору")
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {str(e)}")
            await message.answer(f"❌ Ошибка при получении статистики: {str(e)}")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /stats: {str(e)}")
        await message.answer(messages.ERROR_MESSAGE)


@router.message(Command("test_scenario"))
async def cmd_test_scenario(message: types.Message) -> None:
    """Обработчик команды /test_scenario для тестирования (только для админов).
    
    Позволяет быстро протестировать сценарий.
    """
    try:
        user_telegram_id = message.from_user.id
        
        # Проверяем, является ли пользователь админом
        if not is_admin(user_telegram_id):
            logger.warning(f"Попытка доступа к /test_scenario от пользователя {user_telegram_id}")
            await message.answer(messages.ADMIN_ONLY)
            return
        
        logger.info(f"Администратор {user_telegram_id} запустил тестирование сценария")
        
        await message.answer("🧪 Запускаем тестирование сценария...\n\n📖 Для запуска сценария используйте: /read tarot")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /test_scenario: {str(e)}")
        await message.answer(messages.ERROR_MESSAGE)
