"""Сервис для управления сценариями и проигрывания."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from .reading_repository import ReadingRepository
from .step_repository import StepRepository
from .question_repository import QuestionRepository
from ..models.reading import ReadingCreate, ReadingUpdate
from ..locales import messages

logger = logging.getLogger(__name__)


class ScenarioService:
    """Сервис для работы со сценариями."""

    def __init__(self, bot: Bot):
        """Инициализация сервиса."""
        self.bot = bot

    async def get_user_balance(self, user_id: int) -> Dict[str, int]:
        """Получение баланса пользователя.
        
        Args:
            user_id: ID пользователя в БД
            
        Returns:
            Словарь с количеством бесплатных и платных чтений
        """
        try:
            readings = await ReadingRepository.get_by_user_id(user_id, limit=1000)
            free_count = len([r for r in readings if r.reading_type == "free"])
            paid_count = len([r for r in readings if r.reading_type == "paid"])
            
            logger.info(f"Получен баланс пользователя {user_id}: бесплатные={free_count}, платные={paid_count}")
            return {
                "free_readings": free_count,
                "paid_readings": paid_count
            }
        except Exception as e:
            logger.error(f"Ошибка при получении баланса пользователя {user_id}: {str(e)}")
            return {"free_readings": 0, "paid_readings": 0}

    async def start_scenario(self, user_id: int, payload: Optional[str] = None) -> Optional[int]:
        """Запуск сценария для пользователя.
        
        Args:
            user_id: ID пользователя в БД
            payload: Тип сценария (например, 'tarot', 'reading')
            
        Returns:
            ID чтения или None при ошибке
        """
        try:
            reading_type = payload or "default"
            reading_data = ReadingCreate(
                user_id=user_id,
                reading_type=reading_type,
                status="pending"
            )
            
            reading = await ReadingRepository.create(reading_data)
            logger.info(f"Создано чтение {reading.id} для пользователя {user_id} типа {reading_type}")
            return reading.id
            
        except Exception as e:
            logger.error(f"Ошибка при создании чтения: {str(e)}")
            return None

    async def play_scenario_steps(
        self,
        user_id: int,
        chat_id: int,
        reading_id: int
    ) -> bool:
        """Проигрывание всех шагов сценария последовательно.
        
        Args:
            user_id: ID пользователя в БД
            chat_id: ID чата Telegram
            reading_id: ID чтения
            
        Returns:
            True если успешно, False если произошла ошибка
        """
        try:
            # Получаем все активные шаги
            steps = await StepRepository.get_active_steps()
            
            if not steps:
                logger.warning(f"Нет активных шагов для чтения {reading_id}")
                await self.bot.send_message(
                    chat_id,
                    messages.SCENARIO_ERROR.format(error="Сценарий не содержит шагов")
                )
                return False
            
            # Проходим через каждый шаг
            for step in steps:
                try:
                    await self._play_step(chat_id, step, reading_id)
                    
                    # Получаем задержку (если она есть в description)
                    delay_sec = self._extract_delay(step.description)
                    if delay_sec > 0:
                        await asyncio.sleep(delay_sec)
                        
                except Exception as e:
                    logger.error(f"Ошибка при проигрывании шага {step.id}: {str(e)}")
                    await self.bot.send_message(
                        chat_id,
                        messages.SCENARIO_ERROR.format(error=str(e))
                    )
                    return False
            
            # Завершаем чтение
            update_data = ReadingUpdate(
                status="completed",
                completed_at=datetime.utcnow()
            )
            await ReadingRepository.update(reading_id, update_data)
            
            await self.bot.send_message(chat_id, messages.SCENARIO_COMPLETED)
            logger.info(f"Сценарий чтения {reading_id} успешно завершен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при проигрывании сценария: {str(e)}")
            return False

    async def _play_step(self, chat_id: int, step, reading_id: int) -> None:
        """Проигрывание одного шага.
        
        Args:
            chat_id: ID чата Telegram
            step: Объект шага
            reading_id: ID чтения
        """
        try:
            logger.info(f"Проигрывание шага {step.id} ({step.name})")
            
            # Получаем вопросы для этого шага
            questions = await QuestionRepository.get_by_step_id(step.id)
            
            # Если в description содержится текст, отправляем его
            if step.description:
                # Проверяем, содержит ли описание image_file_id
                if "image_file_id:" in step.description:
                    file_id = self._extract_file_id(step.description)
                    if file_id:
                        try:
                            await self.bot.send_photo(chat_id, file_id)
                        except Exception as e:
                            logger.error(f"Ошибка при отправке фото: {str(e)}")
                    # Отправляем текст после фото (если есть)
                    text = self._extract_text_before_image(step.description)
                    if text.strip():
                        await self.bot.send_message(chat_id, text)
                else:
                    # Просто отправляем текст
                    await self.bot.send_message(chat_id, step.description)
            
            # Обрабатываем вопросы шага
            for question in questions:
                await self._handle_question(chat_id, question, reading_id)
                
        except Exception as e:
            logger.error(f"Ошибка при проигрывании шага {step.id}: {str(e)}")
            raise

    async def _handle_question(self, chat_id: int, question, reading_id: int) -> None:
        """Обработка вопроса.
        
        Args:
            chat_id: ID чата Telegram
            question: Объект вопроса
            reading_id: ID чтения
        """
        try:
            logger.info(f"Обработка вопроса {question.id} ({question.question_text})")
            
            if question.question_type == "text":
                # Текстовый вопрос - просто отправляем сообщение
                await self.bot.send_message(
                    chat_id,
                    f"{messages.QUESTION_TEXT_INPUT}\n\n{question.question_text}"
                )
            elif question.question_type == "single_choice":
                # Выбор одного варианта - inline кнопки
                await self._send_single_choice_question(chat_id, question)
            elif question.question_type == "multiple_choice":
                # Выбор нескольких вариантов - keyboard кнопки
                await self._send_multiple_choice_question(chat_id, question)
            else:
                # Неизвестный тип вопроса
                await self.bot.send_message(chat_id, question.question_text)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке вопроса {question.id}: {str(e)}")
            raise

    async def _send_single_choice_question(self, chat_id: int, question) -> None:
        """Отправка вопроса с одним вариантом ответа (inline кнопки).
        
        Args:
            chat_id: ID чата Telegram
            question: Объект вопроса
        """
        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            
            if question.options:
                for option in question.options:
                    text = option.get("text", "Опция")
                    callback_data = option.get("payload", text)
                    button = InlineKeyboardButton(
                        text=text,
                        callback_data=f"answer_{question.id}_{callback_data}"
                    )
                    keyboard.inline_keyboard.append([button])
            
            await self.bot.send_message(
                chat_id,
                f"{messages.QUESTION_SELECTION}\n\n{question.question_text}",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке single choice вопроса: {str(e)}")
            raise

    async def _send_multiple_choice_question(self, chat_id: int, question) -> None:
        """Отправка вопроса с несколькими вариантами ответов (keyboard кнопки).
        
        Args:
            chat_id: ID чата Telegram
            question: Объект вопроса
        """
        try:
            keyboard = ReplyKeyboardMarkup(keyboard=[])
            
            if question.options:
                row = []
                for i, option in enumerate(question.options):
                    text = option.get("text", "Опция")
                    button = KeyboardButton(text=text)
                    row.append(button)
                    
                    # Максимум 2 кнопки в строке для multiple choice
                    if len(row) >= 2 or i == len(question.options) - 1:
                        keyboard.keyboard.append(row)
                        row = []
            
            # Добавляем кнопку пропуска если вопрос не обязателен
            if not question.is_required:
                keyboard.keyboard.append([KeyboardButton(text=messages.BUTTON_SKIP)])
            
            keyboard.resize_keyboard = True
            keyboard.one_time_keyboard = True
            
            await self.bot.send_message(
                chat_id,
                f"{messages.QUESTION_SELECTION}\n\n{question.question_text}",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке multiple choice вопроса: {str(e)}")
            raise

    @staticmethod
    def _extract_delay(description: Optional[str]) -> int:
        """Извлечение задержки из описания.
        
        Args:
            description: Описание шага
            
        Returns:
            Задержка в секундах
        """
        if not description:
            return 0
        
        try:
            if "delay_sec:" in description:
                parts = description.split("delay_sec:")
                if len(parts) > 1:
                    delay_str = parts[1].split("|")[0].strip()
                    return int(delay_str)
        except Exception as e:
            logger.error(f"Ошибка при извлечении задержки: {str(e)}")
        
        return 0

    @staticmethod
    def _extract_file_id(description: Optional[str]) -> Optional[str]:
        """Извлечение file_id фото из описания.
        
        Args:
            description: Описание шага
            
        Returns:
            File ID или None
        """
        if not description:
            return None
        
        try:
            if "image_file_id:" in description:
                parts = description.split("image_file_id:")
                if len(parts) > 1:
                    file_id = parts[1].split("|")[0].strip()
                    return file_id
        except Exception as e:
            logger.error(f"Ошибка при извлечении file_id: {str(e)}")
        
        return None

    @staticmethod
    def _extract_text_before_image(description: Optional[str]) -> str:
        """Извлечение текста перед фото.
        
        Args:
            description: Описание шага
            
        Returns:
            Текст или пустая строка
        """
        if not description:
            return ""
        
        try:
            if "image_file_id:" in description:
                parts = description.split("image_file_id:")
                if len(parts) > 0:
                    return parts[0].strip()
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста: {str(e)}")
        
        return description
