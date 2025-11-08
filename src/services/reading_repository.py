"""Репозиторий для работы с чтениями."""

import logging
from typing import Optional, List
from datetime import datetime

from ..models.reading import Reading, ReadingCreate, ReadingUpdate
from .database import fetch_one, fetch_many, execute_query, fetch_val

logger = logging.getLogger(__name__)


class ReadingRepository:
    """Репозиторий для управления чтениями."""

    @staticmethod
    async def create(reading_data: ReadingCreate) -> Reading:
        """Создание нового чтения."""
        try:
            query = """
                INSERT INTO readings (user_id, reading_type, reading_payload, status, completed_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, user_id, reading_type, reading_payload, status, created_at, completed_at
            """
            result = await fetch_one(
                query,
                reading_data.user_id,
                reading_data.reading_type,
                reading_data.reading_payload,
                reading_data.status,
                reading_data.completed_at
            )
            
            if not result:
                raise RuntimeError("Не удалось создать чтение")
            
            logger.info(f"Создано чтение для пользователя: {reading_data.user_id}")
            return Reading(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при создании чтения: {str(e)}")
            raise RuntimeError(f"Ошибка при создании чтения: {str(e)}")

    @staticmethod
    async def get_by_id(reading_id: int) -> Optional[Reading]:
        """Получение чтения по ID."""
        try:
            query = """
                SELECT id, user_id, reading_type, reading_payload, status, created_at, completed_at
                FROM readings
                WHERE id = $1
            """
            result = await fetch_one(query, reading_id)
            return Reading(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении чтения по ID {reading_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении чтения: {str(e)}")

    @staticmethod
    async def get_by_user_id(user_id: int, limit: int = 50, offset: int = 0) -> List[Reading]:
        """Получение чтений пользователя с пагинацией."""
        try:
            query = """
                SELECT id, user_id, reading_type, reading_payload, status, created_at, completed_at
                FROM readings
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """
            results = await fetch_many(query, user_id, limit, offset)
            return [Reading(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении чтений пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении чтений: {str(e)}")

    @staticmethod
    async def get_by_user_id_and_type(user_id: int, reading_type: str, limit: int = 50, offset: int = 0) -> List[Reading]:
        """Получение чтений пользователя определенного типа."""
        try:
            query = """
                SELECT id, user_id, reading_type, reading_payload, status, created_at, completed_at
                FROM readings
                WHERE user_id = $1 AND reading_type = $2
                ORDER BY created_at DESC
                LIMIT $3 OFFSET $4
            """
            results = await fetch_many(query, user_id, reading_type, limit, offset)
            return [Reading(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении чтений типа {reading_type} пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении чтений: {str(e)}")

    @staticmethod
    async def get_by_status(status: str, limit: int = 50, offset: int = 0) -> List[Reading]:
        """Получение чтений по статусу."""
        try:
            query = """
                SELECT id, user_id, reading_type, reading_payload, status, created_at, completed_at
                FROM readings
                WHERE status = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """
            results = await fetch_many(query, status, limit, offset)
            return [Reading(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении чтений со статусом {status}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении чтений: {str(e)}")

    @staticmethod
    async def update(reading_id: int, reading_data: ReadingUpdate) -> Optional[Reading]:
        """Обновление данных чтения."""
        try:
            # Динамическое формирование запроса на основе переданных данных
            update_fields = []
            args = []
            arg_index = 1

            if reading_data.reading_type is not None:
                update_fields.append(f"reading_type = ${arg_index}")
                args.append(reading_data.reading_type)
                arg_index += 1

            if reading_data.reading_payload is not None:
                update_fields.append(f"reading_payload = ${arg_index}")
                args.append(reading_data.reading_payload)
                arg_index += 1

            if reading_data.status is not None:
                update_fields.append(f"status = ${arg_index}")
                args.append(reading_data.status)
                arg_index += 1

            if reading_data.completed_at is not None:
                update_fields.append(f"completed_at = ${arg_index}")
                args.append(reading_data.completed_at)
                arg_index += 1

            if not update_fields:
                # Нет полей для обновления
                return await ReadingRepository.get_by_id(reading_id)

            args.append(reading_id)
            
            query = f"""
                UPDATE readings
                SET {', '.join(update_fields)}
                WHERE id = ${arg_index}
                RETURNING id, user_id, reading_type, reading_payload, status, created_at, completed_at
            """
            
            result = await fetch_one(query, *args)
            
            if not result:
                return None
            
            logger.info(f"Обновлено чтение с ID: {reading_id}")
            return Reading(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении чтения {reading_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при обновлении чтения: {str(e)}")

    @staticmethod
    async def complete_reading(reading_id: int) -> Optional[Reading]:
        """Завершение чтения."""
        try:
            query = """
                UPDATE readings
                SET status = 'completed', completed_at = NOW()
                WHERE id = $1
                RETURNING id, user_id, reading_type, reading_payload, status, created_at, completed_at
            """
            
            result = await fetch_one(query, reading_id)
            
            if not result:
                return None
            
            logger.info(f"Завершено чтение с ID: {reading_id}")
            return Reading(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при завершении чтения {reading_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при завершении чтения: {str(e)}")

    @staticmethod
    async def delete(reading_id: int) -> bool:
        """Удаление чтения."""
        try:
            query = "DELETE FROM readings WHERE id = $1"
            result = await execute_query(query, reading_id)
            
            # Проверяем, была ли удалена хотя бы одна запись
            deleted = "DELETE 1" in result
            
            if deleted:
                logger.info(f"Удалено чтение с ID: {reading_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Ошибка при удалении чтения {reading_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при удалении чтения: {str(e)}")

    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> List[Reading]:
        """Получение списка всех чтений с пагинацией."""
        try:
            query = """
                SELECT id, user_id, reading_type, reading_payload, status, created_at, completed_at
                FROM readings
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            results = await fetch_many(query, limit, offset)
            return [Reading(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка чтений: {str(e)}")
            raise RuntimeError(f"Ошибка при получении списка чтений: {str(e)}")

    @staticmethod
    async def get_total_count() -> int:
        """Получение общего количества чтений."""
        try:
            query = "SELECT COUNT(*) FROM readings"
            result = await fetch_val(query)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества чтений: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества чтений: {str(e)}")

    @staticmethod
    async def get_user_reading_count(user_id: int) -> int:
        """Получение количества чтений пользователя."""
        try:
            query = "SELECT COUNT(*) FROM readings WHERE user_id = $1"
            result = await fetch_val(query, user_id)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества чтений пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества чтений: {str(e)}")

    @staticmethod
    async def get_latest_user_reading(user_id: int, reading_type: Optional[str] = None) -> Optional[Reading]:
        """Получение последнего чтения пользователя."""
        try:
            if reading_type:
                query = """
                    SELECT id, user_id, reading_type, reading_payload, status, created_at, completed_at
                    FROM readings
                    WHERE user_id = $1 AND reading_type = $2
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                result = await fetch_one(query, user_id, reading_type)
            else:
                query = """
                    SELECT id, user_id, reading_type, reading_payload, status, created_at, completed_at
                    FROM readings
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                result = await fetch_one(query, user_id)
            
            return Reading(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении последнего чтения пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении последнего чтения: {str(e)}")