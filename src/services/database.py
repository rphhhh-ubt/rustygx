"""Сервис для работы с базой данных."""

import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager

from ..config import settings

logger = logging.getLogger(__name__)

# Глобальный пул соединений
pool: Optional[asyncpg.Pool] = None


async def init_database() -> None:
    """Инициализация пула соединений с базой данных."""
    global pool
    try:
        logger.info("Инициализация пула соединений с базой данных...")
        pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
            server_settings={
                "application_name": "telegram_bot",
                "timezone": "UTC"
            }
        )
        logger.info("Пул соединений с базой данных успешно инициализирован")
    except Exception as e:
        logger.error(f"Ошибка при инициализации пула соединений: {str(e)}")
        raise


async def close_database() -> None:
    """Закрытие пула соединений с базой данных."""
    global pool
    try:
        if pool:
            logger.info("Закрытие пула соединений с базой данных...")
            await pool.close()
            pool = None
            logger.info("Пул соединений с базой данных закрыт")
    except Exception as e:
        logger.error(f"Ошибка при закрытии пула соединений: {str(e)}")
        raise


@asynccontextmanager
async def get_connection():
    """Контекстный менеджер для получения соединения из пула."""
    if not pool:
        raise RuntimeError("Пул соединений не инициализирован. Вызовите init_database()")
    
    conn = None
    try:
        conn = await pool.acquire()
        yield conn
    except Exception as e:
        logger.error(f"Ошибка при работе с соединением: {str(e)}")
        raise
    finally:
        if conn:
            await pool.release(conn)


async def execute_query(query: str, *args) -> str:
    """Выполнение запроса без возврата результата (INSERT, UPDATE, DELETE)."""
    async with get_connection() as conn:
        try:
            result = await conn.execute(query, *args)
            logger.debug(f"Выполнен запрос: {query[:100]}... с аргументами: {args}")
            return result
        except asyncpg.PostgresError as e:
            logger.error(f"Ошибка PostgreSQL при выполнении запроса: {str(e)}")
            raise RuntimeError(f"Ошибка базы данных: {str(e)}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при выполнении запроса: {str(e)}")
            raise RuntimeError(f"Ошибка выполнения запроса: {str(e)}")


async def fetch_one(query: str, *args) -> Optional[dict]:
    """Получение одной записи из базы данных."""
    async with get_connection() as conn:
        try:
            result = await conn.fetchrow(query, *args)
            logger.debug(f"Получена запись: {query[:100]}... с аргументами: {args}")
            return dict(result) if result else None
        except asyncpg.PostgresError as e:
            logger.error(f"Ошибка PostgreSQL при получении записи: {str(e)}")
            raise RuntimeError(f"Ошибка базы данных: {str(e)}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при получении записи: {str(e)}")
            raise RuntimeError(f"Ошибка выполнения запроса: {str(e)}")


async def fetch_many(query: str, *args) -> list[dict]:
    """Получение множества записей из базы данных."""
    async with get_connection() as conn:
        try:
            result = await conn.fetch(query, *args)
            logger.debug(f"Получено {len(result)} записей: {query[:100]}... с аргументами: {args}")
            return [dict(row) for row in result]
        except asyncpg.PostgresError as e:
            logger.error(f"Ошибка PostgreSQL при получении записей: {str(e)}")
            raise RuntimeError(f"Ошибка базы данных: {str(e)}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при получении записей: {str(e)}")
            raise RuntimeError(f"Ошибка выполнения запроса: {str(e)}")


async def fetch_val(query: str, *args) -> any:
    """Получение одного значения из базы данных."""
    async with get_connection() as conn:
        try:
            result = await conn.fetchval(query, *args)
            logger.debug(f"Получено значение: {query[:100]}... с аргументами: {args}")
            return result
        except asyncpg.PostgresError as e:
            logger.error(f"Ошибка PostgreSQL при получении значения: {str(e)}")
            raise RuntimeError(f"Ошибка базы данных: {str(e)}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при получении значения: {str(e)}")
            raise RuntimeError(f"Ошибка выполнения запроса: {str(e)}")


async def execute_transaction(queries: list[tuple[str, tuple]]) -> list:
    """Выполнение транзакции с несколькими запросами."""
    async with get_connection() as conn:
        try:
            async with conn.transaction():
                results = []
                for query, args in queries:
                    if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                        result = await conn.execute(query, *args)
                        results.append(result)
                    else:
                        result = await conn.fetchrow(query, *args)
                        results.append(dict(result) if result else None)
                logger.debug(f"Выполнена транзакция из {len(queries)} запросов")
                return results
        except asyncpg.PostgresError as e:
            logger.error(f"Ошибка PostgreSQL при выполнении транзакции: {str(e)}")
            raise RuntimeError(f"Ошибка базы данных при выполнении транзакции: {str(e)}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при выполнении транзакции: {str(e)}")
            raise RuntimeError(f"Ошибка выполнения транзакции: {str(e)}")


def is_database_initialized() -> bool:
    """Проверка инициализирован ли пул соединений."""
    return pool is not None


async def test_connection() -> bool:
    """Проверка соединения с базой данных."""
    try:
        await fetch_val("SELECT 1")
        logger.info("Соединение с базой данных успешно проверено")
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке соединения с базой данных: {str(e)}")
        return False