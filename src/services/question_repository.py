"""Репозиторий для работы с вопросами."""

import logging
from typing import Optional, List

from ..models.question import Question, QuestionCreate, QuestionUpdate
from .database import fetch_one, fetch_many, execute_query, fetch_val

logger = logging.getLogger(__name__)


class QuestionRepository:
    """Репозиторий для управления вопросами."""

    @staticmethod
    async def create(question_data: QuestionCreate) -> Question:
        """Создание нового вопроса."""
        try:
            query = """
                INSERT INTO questions (step_id, question_text, question_type, options, question_order, is_required)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
            """
            result = await fetch_one(
                query,
                question_data.step_id,
                question_data.question_text,
                question_data.question_type,
                question_data.options,
                question_data.question_order,
                question_data.is_required
            )
            
            if not result:
                raise RuntimeError("Не удалось создать вопрос")
            
            logger.info(f"Создан вопрос для шага {question_data.step_id}")
            return Question(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при создании вопроса: {str(e)}")
            raise RuntimeError(f"Ошибка при создании вопроса: {str(e)}")

    @staticmethod
    async def get_by_id(question_id: int) -> Optional[Question]:
        """Получение вопроса по ID."""
        try:
            query = """
                SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                FROM questions
                WHERE id = $1
            """
            result = await fetch_one(query, question_id)
            return Question(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении вопроса по ID {question_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении вопроса: {str(e)}")

    @staticmethod
    async def get_by_step_id(step_id: int) -> List[Question]:
        """Получение вопросов шага, отсортированных по порядковому номеру."""
        try:
            query = """
                SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                FROM questions
                WHERE step_id = $1
                ORDER BY question_order ASC
            """
            results = await fetch_many(query, step_id)
            return [Question(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении вопросов шага {step_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении вопросов: {str(e)}")

    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> List[Question]:
        """Получение списка всех вопросов с пагинацией."""
        try:
            query = """
                SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                FROM questions
                ORDER BY step_id, question_order ASC
                LIMIT $1 OFFSET $2
            """
            results = await fetch_many(query, limit, offset)
            return [Question(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка вопросов: {str(e)}")
            raise RuntimeError(f"Ошибка при получении списка вопросов: {str(e)}")

    @staticmethod
    async def get_by_type(question_type: str, limit: int = 50, offset: int = 0) -> List[Question]:
        """Получение вопросов по типу."""
        try:
            query = """
                SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                FROM questions
                WHERE question_type = $1
                ORDER BY step_id, question_order ASC
                LIMIT $2 OFFSET $3
            """
            results = await fetch_many(query, question_type, limit, offset)
            return [Question(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении вопросов типа {question_type}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении вопросов: {str(e)}")

    @staticmethod
    async def get_required_questions(step_id: Optional[int] = None) -> List[Question]:
        """Получение обязательных вопросов."""
        try:
            if step_id:
                query = """
                    SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                    FROM questions
                    WHERE step_id = $1 AND is_required = TRUE
                    ORDER BY question_order ASC
                """
                results = await fetch_many(query, step_id)
            else:
                query = """
                    SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                    FROM questions
                    WHERE is_required = TRUE
                    ORDER BY step_id, question_order ASC
                """
                results = await fetch_many(query)
            
            return [Question(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении обязательных вопросов: {str(e)}")
            raise RuntimeError(f"Ошибка при получении вопросов: {str(e)}")

    @staticmethod
    async def update(question_id: int, question_data: QuestionUpdate) -> Optional[Question]:
        """Обновление данных вопроса."""
        try:
            # Динамическое формирование запроса на основе переданных данных
            update_fields = []
            args = []
            arg_index = 1

            if question_data.question_text is not None:
                update_fields.append(f"question_text = ${arg_index}")
                args.append(question_data.question_text)
                arg_index += 1

            if question_data.question_type is not None:
                update_fields.append(f"question_type = ${arg_index}")
                args.append(question_data.question_type)
                arg_index += 1

            if question_data.options is not None:
                update_fields.append(f"options = ${arg_index}")
                args.append(question_data.options)
                arg_index += 1

            if question_data.question_order is not None:
                update_fields.append(f"question_order = ${arg_index}")
                args.append(question_data.question_order)
                arg_index += 1

            if question_data.is_required is not None:
                update_fields.append(f"is_required = ${arg_index}")
                args.append(question_data.is_required)
                arg_index += 1

            if not update_fields:
                # Нет полей для обновления
                return await QuestionRepository.get_by_id(question_id)

            args.append(question_id)
            
            query = f"""
                UPDATE questions
                SET {', '.join(update_fields)}
                WHERE id = ${arg_index}
                RETURNING id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
            """
            
            result = await fetch_one(query, *args)
            
            if not result:
                return None
            
            logger.info(f"Обновлен вопрос с ID: {question_id}")
            return Question(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении вопроса {question_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при обновлении вопроса: {str(e)}")

    @staticmethod
    async def delete(question_id: int) -> bool:
        """Удаление вопроса."""
        try:
            query = "DELETE FROM questions WHERE id = $1"
            result = await execute_query(query, question_id)
            
            # Проверяем, была ли удалена хотя бы одна запись
            deleted = "DELETE 1" in result
            
            if deleted:
                logger.info(f"Удален вопрос с ID: {question_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Ошибка при удалении вопроса {question_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при удалении вопроса: {str(e)}")

    @staticmethod
    async def delete_by_step_id(step_id: int) -> int:
        """Удаление всех вопросов шага."""
        try:
            query = "DELETE FROM questions WHERE step_id = $1"
            result = await execute_query(query, step_id)
            
            # Извлекаем количество удаленных записей
            import re
            match = re.search(r'DELETE (\d+)', result)
            deleted_count = int(match.group(1)) if match else 0
            
            if deleted_count > 0:
                logger.info(f"Удалено {deleted_count} вопросов для шага {step_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Ошибка при удалении вопросов шага {step_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при удалении вопросов: {str(e)}")

    @staticmethod
    async def get_total_count() -> int:
        """Получение общего количества вопросов."""
        try:
            query = "SELECT COUNT(*) FROM questions"
            result = await fetch_val(query)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества вопросов: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества вопросов: {str(e)}")

    @staticmethod
    async def get_step_question_count(step_id: int) -> int:
        """Получение количества вопросов шага."""
        try:
            query = "SELECT COUNT(*) FROM questions WHERE step_id = $1"
            result = await fetch_val(query, step_id)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества вопросов шага {step_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества вопросов: {str(e)}")

    @staticmethod
    async def get_next_question_order(step_id: int) -> int:
        """Получение следующего порядкового номера для вопроса в шаге."""
        try:
            query = "SELECT COALESCE(MAX(question_order), 0) + 1 FROM questions WHERE step_id = $1"
            result = await fetch_val(query, step_id)
            return result or 1
            
        except Exception as e:
            logger.error(f"Ошибка при получении следующего порядкового номера: {str(e)}")
            raise RuntimeError(f"Ошибка при получении порядкового номера: {str(e)}")

    @staticmethod
    async def reorder_questions(step_id: int, question_orders: dict[int, int]) -> bool:
        """Изменение порядка вопросов в шаге."""
        try:
            # Проверяем, что все порядковые номера уникальны
            if len(set(question_orders.values())) != len(question_orders):
                raise ValueError("Порядковые номера должны быть уникальными")
            
            # Обновляем каждый вопрос
            for question_id, new_order in question_orders.items():
                query = "UPDATE questions SET question_order = $1 WHERE id = $2 AND step_id = $3"
                await execute_query(query, new_order, question_id, step_id)
            
            logger.info(f"Изменен порядок вопросов для шага {step_id}: {question_orders}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при изменении порядка вопросов: {str(e)}")
            raise RuntimeError(f"Ошибка при изменении порядка вопросов: {str(e)}")

    @staticmethod
    async def get_questions_by_step_ids(step_ids: List[int]) -> List[Question]:
        """Получение вопросов для нескольких шагов."""
        try:
            if not step_ids:
                return []
            
            # Формируем плейсхолдеры для IN запроса
            placeholders = ', '.join(f'${i+1}' for i in range(len(step_ids)))
            
            query = f"""
                SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                FROM questions
                WHERE step_id IN ({placeholders})
                ORDER BY step_id, question_order ASC
            """
            
            results = await fetch_many(query, *step_ids)
            return [Question(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении вопросов для шагов {step_ids}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении вопросов: {str(e)}")