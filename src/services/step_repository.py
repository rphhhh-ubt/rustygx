"""Репозиторий для работы с шагами."""

import logging
from typing import Optional, List

from ..models.step import Step, StepCreate, StepUpdate, StepWithQuestions
from ..models.question import Question
from .database import fetch_one, fetch_many, execute_query, fetch_val

logger = logging.getLogger(__name__)


class StepRepository:
    """Репозиторий для управления шагами."""

    @staticmethod
    async def create(step_data: StepCreate) -> Step:
        """Создание нового шага."""
        try:
            query = """
                INSERT INTO steps (name, description, step_order, is_active)
                VALUES ($1, $2, $3, $4)
                RETURNING id, name, description, step_order, is_active, created_at, updated_at
            """
            result = await fetch_one(
                query,
                step_data.name,
                step_data.description,
                step_data.step_order,
                step_data.is_active
            )
            
            if not result:
                raise RuntimeError("Не удалось создать шаг")
            
            logger.info(f"Создан шаг: {step_data.name}")
            return Step(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при создании шага: {str(e)}")
            raise RuntimeError(f"Ошибка при создании шага: {str(e)}")

    @staticmethod
    async def get_by_id(step_id: int) -> Optional[Step]:
        """Получение шага по ID."""
        try:
            query = """
                SELECT id, name, description, step_order, is_active, created_at, updated_at
                FROM steps
                WHERE id = $1
            """
            result = await fetch_one(query, step_id)
            return Step(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении шага по ID {step_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении шага: {str(e)}")

    @staticmethod
    async def get_by_order(step_order: int) -> Optional[Step]:
        """Получение шага по порядковому номеру."""
        try:
            query = """
                SELECT id, name, description, step_order, is_active, created_at, updated_at
                FROM steps
                WHERE step_order = $1
            """
            result = await fetch_one(query, step_order)
            return Step(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении шага по порядковому номеру {step_order}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении шага: {str(e)}")

    @staticmethod
    async def get_active_steps() -> List[Step]:
        """Получение всех активных шагов, отсортированных по порядковому номеру."""
        try:
            query = """
                SELECT id, name, description, step_order, is_active, created_at, updated_at
                FROM steps
                WHERE is_active = TRUE
                ORDER BY step_order ASC
            """
            results = await fetch_many(query)
            return [Step(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении активных шагов: {str(e)}")
            raise RuntimeError(f"Ошибка при получении шагов: {str(e)}")

    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> List[Step]:
        """Получение списка всех шагов с пагинацией."""
        try:
            query = """
                SELECT id, name, description, step_order, is_active, created_at, updated_at
                FROM steps
                ORDER BY step_order ASC
                LIMIT $1 OFFSET $2
            """
            results = await fetch_many(query, limit, offset)
            return [Step(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка шагов: {str(e)}")
            raise RuntimeError(f"Ошибка при получении списка шагов: {str(e)}")

    @staticmethod
    async def get_with_questions(step_id: int) -> Optional[StepWithQuestions]:
        """Получение шага с вопросами."""
        try:
            # Получаем шаг
            step_query = """
                SELECT id, name, description, step_order, is_active, created_at, updated_at
                FROM steps
                WHERE id = $1
            """
            step_result = await fetch_one(step_query, step_id)
            
            if not step_result:
                return None
            
            # Получаем вопросы для шага
            questions_query = """
                SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                FROM questions
                WHERE step_id = $1
                ORDER BY question_order ASC
            """
            questions_results = await fetch_many(questions_query, step_id)
            questions = [Question(**result) for result in questions_results]
            
            # Создаем объект StepWithQuestions
            step_data = Step(**step_result)
            return StepWithQuestions(**step_data.dict(), questions=questions)
            
        except Exception as e:
            logger.error(f"Ошибка при получении шага с вопросами {step_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении шага с вопросами: {str(e)}")

    @staticmethod
    async def get_active_with_questions() -> List[StepWithQuestions]:
        """Получение всех активных шагов с вопросами."""
        try:
            # Получаем активные шаги
            steps_query = """
                SELECT id, name, description, step_order, is_active, created_at, updated_at
                FROM steps
                WHERE is_active = TRUE
                ORDER BY step_order ASC
            """
            steps_results = await fetch_many(steps_query)
            
            steps_with_questions = []
            
            for step_result in steps_results:
                step_id = step_result['id']
                
                # Получаем вопросы для шага
                questions_query = """
                    SELECT id, step_id, question_text, question_type, options, question_order, is_required, created_at, updated_at
                    FROM questions
                    WHERE step_id = $1
                    ORDER BY question_order ASC
                """
                questions_results = await fetch_many(questions_query, step_id)
                questions = [Question(**result) for result in questions_results]
                
                # Создаем объект StepWithQuestions
                step_data = Step(**step_result)
                step_with_questions = StepWithQuestions(**step_data.dict(), questions=questions)
                steps_with_questions.append(step_with_questions)
            
            return steps_with_questions
            
        except Exception as e:
            logger.error(f"Ошибка при получении активных шагов с вопросами: {str(e)}")
            raise RuntimeError(f"Ошибка при получении шагов с вопросами: {str(e)}")

    @staticmethod
    async def update(step_id: int, step_data: StepUpdate) -> Optional[Step]:
        """Обновление данных шага."""
        try:
            # Динамическое формирование запроса на основе переданных данных
            update_fields = []
            args = []
            arg_index = 1

            if step_data.name is not None:
                update_fields.append(f"name = ${arg_index}")
                args.append(step_data.name)
                arg_index += 1

            if step_data.description is not None:
                update_fields.append(f"description = ${arg_index}")
                args.append(step_data.description)
                arg_index += 1

            if step_data.step_order is not None:
                update_fields.append(f"step_order = ${arg_index}")
                args.append(step_data.step_order)
                arg_index += 1

            if step_data.is_active is not None:
                update_fields.append(f"is_active = ${arg_index}")
                args.append(step_data.is_active)
                arg_index += 1

            if not update_fields:
                # Нет полей для обновления
                return await StepRepository.get_by_id(step_id)

            args.append(step_id)
            
            query = f"""
                UPDATE steps
                SET {', '.join(update_fields)}
                WHERE id = ${arg_index}
                RETURNING id, name, description, step_order, is_active, created_at, updated_at
            """
            
            result = await fetch_one(query, *args)
            
            if not result:
                return None
            
            logger.info(f"Обновлен шаг с ID: {step_id}")
            return Step(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении шага {step_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при обновлении шага: {str(e)}")

    @staticmethod
    async def delete(step_id: int) -> bool:
        """Удаление шага."""
        try:
            query = "DELETE FROM steps WHERE id = $1"
            result = await execute_query(query, step_id)
            
            # Проверяем, была ли удалена хотя бы одна запись
            deleted = "DELETE 1" in result
            
            if deleted:
                logger.info(f"Удален шаг с ID: {step_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Ошибка при удалении шага {step_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при удалении шага: {str(e)}")

    @staticmethod
    async def get_total_count() -> int:
        """Получение общего количества шагов."""
        try:
            query = "SELECT COUNT(*) FROM steps"
            result = await fetch_val(query)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества шагов: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества шагов: {str(e)}")

    @staticmethod
    async def get_active_count() -> int:
        """Получение количества активных шагов."""
        try:
            query = "SELECT COUNT(*) FROM steps WHERE is_active = TRUE"
            result = await fetch_val(query)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества активных шагов: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества шагов: {str(e)}")

    @staticmethod
    async def get_next_step_order() -> int:
        """Получение следующего порядкового номера для шага."""
        try:
            query = "SELECT COALESCE(MAX(step_order), 0) + 1 FROM steps"
            result = await fetch_val(query)
            return result or 1
            
        except Exception as e:
            logger.error(f"Ошибка при получении следующего порядкового номера: {str(e)}")
            raise RuntimeError(f"Ошибка при получении порядкового номера: {str(e)}")

    @staticmethod
    async def reorder_steps(step_orders: dict[int, int]) -> bool:
        """Изменение порядка шагов."""
        try:
            # Проверяем, что все порядковые номера уникальны
            if len(set(step_orders.values())) != len(step_orders):
                raise ValueError("Порядковые номера должны быть уникальными")
            
            # Обновляем каждый шаг
            for step_id, new_order in step_orders.items():
                query = "UPDATE steps SET step_order = $1 WHERE id = $2"
                await execute_query(query, new_order, step_id)
            
            logger.info(f"Изменен порядок шагов: {step_orders}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при изменении порядка шагов: {str(e)}")
            raise RuntimeError(f"Ошибка при изменении порядка шагов: {str(e)}")