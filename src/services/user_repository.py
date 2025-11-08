"""Репозиторий для работы с пользователями."""

import logging
from typing import Optional, List

from ..models.user import User, UserCreate, UserUpdate
from .database import fetch_one, fetch_many, execute_query, fetch_val

logger = logging.getLogger(__name__)


class UserRepository:
    """Репозиторий для управления пользователями."""

    @staticmethod
    async def create(user_data: UserCreate) -> User:
        """Создание нового пользователя."""
        try:
            query = """
                INSERT INTO bot_users (telegram_id, first_name, last_name, username, is_bot)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, telegram_id, first_name, last_name, username, is_bot, created_at, updated_at
            """
            result = await fetch_one(
                query,
                user_data.telegram_id,
                user_data.first_name,
                user_data.last_name,
                user_data.username,
                user_data.is_bot
            )
            
            if not result:
                raise RuntimeError("Не удалось создать пользователя")
            
            logger.info(f"Создан пользователь с telegram_id: {user_data.telegram_id}")
            return User(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {str(e)}")
            raise RuntimeError(f"Ошибка при создании пользователя: {str(e)}")

    @staticmethod
    async def get_by_id(user_id: int) -> Optional[User]:
        """Получение пользователя по ID."""
        try:
            query = """
                SELECT id, telegram_id, first_name, last_name, username, is_bot, created_at, updated_at
                FROM bot_users
                WHERE id = $1
            """
            result = await fetch_one(query, user_id)
            return User(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по ID {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении пользователя: {str(e)}")

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> Optional[User]:
        """Получение пользователя по telegram_id."""
        try:
            query = """
                SELECT id, telegram_id, first_name, last_name, username, is_bot, created_at, updated_at
                FROM bot_users
                WHERE telegram_id = $1
            """
            result = await fetch_one(query, telegram_id)
            return User(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по telegram_id {telegram_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении пользователя: {str(e)}")

    @staticmethod
    async def get_by_username(username: str) -> Optional[User]:
        """Получение пользователя по username."""
        try:
            query = """
                SELECT id, telegram_id, first_name, last_name, username, is_bot, created_at, updated_at
                FROM bot_users
                WHERE username = $1
            """
            result = await fetch_one(query, username)
            return User(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по username {username}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении пользователя: {str(e)}")

    @staticmethod
    async def update(user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Обновление данных пользователя."""
        try:
            # Динамическое формирование запроса на основе переданных данных
            update_fields = []
            args = []
            arg_index = 1

            if user_data.first_name is not None:
                update_fields.append(f"first_name = ${arg_index}")
                args.append(user_data.first_name)
                arg_index += 1

            if user_data.last_name is not None:
                update_fields.append(f"last_name = ${arg_index}")
                args.append(user_data.last_name)
                arg_index += 1

            if user_data.username is not None:
                update_fields.append(f"username = ${arg_index}")
                args.append(user_data.username)
                arg_index += 1

            if user_data.is_bot is not None:
                update_fields.append(f"is_bot = ${arg_index}")
                args.append(user_data.is_bot)
                arg_index += 1

            if not update_fields:
                # Нет полей для обновления
                return await UserRepository.get_by_id(user_id)

            args.append(user_id)
            
            query = f"""
                UPDATE bot_users
                SET {', '.join(update_fields)}
                WHERE id = ${arg_index}
                RETURNING id, telegram_id, first_name, last_name, username, is_bot, created_at, updated_at
            """
            
            result = await fetch_one(query, *args)
            
            if not result:
                return None
            
            logger.info(f"Обновлен пользователь с ID: {user_id}")
            return User(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при обновлении пользователя: {str(e)}")

    @staticmethod
    async def delete(user_id: int) -> bool:
        """Удаление пользователя."""
        try:
            query = "DELETE FROM bot_users WHERE id = $1"
            result = await execute_query(query, user_id)
            
            # Проверяем, была ли удалена хотя бы одна запись
            deleted = "DELETE 1" in result
            
            if deleted:
                logger.info(f"Удален пользователь с ID: {user_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при удалении пользователя: {str(e)}")

    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> List[User]:
        """Получение списка всех пользователей с пагинацией."""
        try:
            query = """
                SELECT id, telegram_id, first_name, last_name, username, is_bot, created_at, updated_at
                FROM bot_users
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            results = await fetch_many(query, limit, offset)
            return [User(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка пользователей: {str(e)}")
            raise RuntimeError(f"Ошибка при получении списка пользователей: {str(e)}")

    @staticmethod
    async def get_total_count() -> int:
        """Получение общего количества пользователей."""
        try:
            query = "SELECT COUNT(*) FROM bot_users"
            result = await fetch_val(query)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества пользователей: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества пользователей: {str(e)}")

    @staticmethod
    async def get_or_create(telegram_id: int, user_data: UserCreate) -> User:
        """Получение пользователя или создание нового, если не существует."""
        try:
            # Сначала пытаемся найти пользователя
            existing_user = await UserRepository.get_by_telegram_id(telegram_id)
            if existing_user:
                return existing_user
            
            # Если не нашли, создаем нового
            return await UserRepository.create(user_data)
            
        except Exception as e:
            logger.error(f"Ошибка при получении или создании пользователя: {str(e)}")
            raise RuntimeError(f"Ошибка при получении или создании пользователя: {str(e)}")