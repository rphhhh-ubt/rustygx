"""Репозиторий для работы с платежами."""

import logging
from typing import Optional, List
from decimal import Decimal

from ..models.payment import Payment, PaymentCreate, PaymentUpdate
from .database import fetch_one, fetch_many, execute_query, fetch_val

logger = logging.getLogger(__name__)


class PaymentRepository:
    """Репозиторий для управления платежами."""

    @staticmethod
    async def create(payment_data: PaymentCreate) -> Payment:
        """Создание нового платежа."""
        try:
            query = """
                INSERT INTO payments (user_id, yookassa_payment_id, amount, currency, status, description, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
            """
            result = await fetch_one(
                query,
                payment_data.user_id,
                payment_data.yookassa_payment_id,
                payment_data.amount,
                payment_data.currency,
                payment_data.status,
                payment_data.description,
                payment_data.metadata
            )
            
            if not result:
                raise RuntimeError("Не удалось создать платеж")
            
            logger.info(f"Создан платеж для пользователя: {payment_data.user_id} на сумму {payment_data.amount}")
            return Payment(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {str(e)}")
            raise RuntimeError(f"Ошибка при создании платежа: {str(e)}")

    @staticmethod
    async def get_by_id(payment_id: int) -> Optional[Payment]:
        """Получение платежа по ID."""
        try:
            query = """
                SELECT id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                FROM payments
                WHERE id = $1
            """
            result = await fetch_one(query, payment_id)
            return Payment(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении платежа по ID {payment_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении платежа: {str(e)}")

    @staticmethod
    async def get_by_yookassa_id(yookassa_payment_id: str) -> Optional[Payment]:
        """Получение платежа по Yookassa ID."""
        try:
            query = """
                SELECT id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                FROM payments
                WHERE yookassa_payment_id = $1
            """
            result = await fetch_one(query, yookassa_payment_id)
            return Payment(**result) if result else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении платежа по Yookassa ID {yookassa_payment_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении платежа: {str(e)}")

    @staticmethod
    async def get_by_user_id(user_id: int, limit: int = 50, offset: int = 0) -> List[Payment]:
        """Получение платежей пользователя с пагинацией."""
        try:
            query = """
                SELECT id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                FROM payments
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """
            results = await fetch_many(query, user_id, limit, offset)
            return [Payment(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении платежей пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении платежей: {str(e)}")

    @staticmethod
    async def get_by_status(status: str, limit: int = 50, offset: int = 0) -> List[Payment]:
        """Получение платежей по статусу."""
        try:
            query = """
                SELECT id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                FROM payments
                WHERE status = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """
            results = await fetch_many(query, status, limit, offset)
            return [Payment(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении платежей со статусом {status}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении платежей: {str(e)}")

    @staticmethod
    async def update(payment_id: int, payment_data: PaymentUpdate) -> Optional[Payment]:
        """Обновление данных платежа."""
        try:
            # Динамическое формирование запроса на основе переданных данных
            update_fields = []
            args = []
            arg_index = 1

            if payment_data.yookassa_payment_id is not None:
                update_fields.append(f"yookassa_payment_id = ${arg_index}")
                args.append(payment_data.yookassa_payment_id)
                arg_index += 1

            if payment_data.amount is not None:
                update_fields.append(f"amount = ${arg_index}")
                args.append(payment_data.amount)
                arg_index += 1

            if payment_data.currency is not None:
                update_fields.append(f"currency = ${arg_index}")
                args.append(payment_data.currency)
                arg_index += 1

            if payment_data.status is not None:
                update_fields.append(f"status = ${arg_index}")
                args.append(payment_data.status)
                arg_index += 1

            if payment_data.description is not None:
                update_fields.append(f"description = ${arg_index}")
                args.append(payment_data.description)
                arg_index += 1

            if payment_data.metadata is not None:
                update_fields.append(f"metadata = ${arg_index}")
                args.append(payment_data.metadata)
                arg_index += 1

            if not update_fields:
                # Нет полей для обновления
                return await PaymentRepository.get_by_id(payment_id)

            args.append(payment_id)
            
            query = f"""
                UPDATE payments
                SET {', '.join(update_fields)}
                WHERE id = ${arg_index}
                RETURNING id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
            """
            
            result = await fetch_one(query, *args)
            
            if not result:
                return None
            
            logger.info(f"Обновлен платеж с ID: {payment_id}")
            return Payment(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении платежа {payment_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при обновлении платежа: {str(e)}")

    @staticmethod
    async def update_status(payment_id: int, status: str, yookassa_payment_id: Optional[str] = None) -> Optional[Payment]:
        """Обновление статуса платежа."""
        try:
            if yookassa_payment_id:
                query = """
                    UPDATE payments
                    SET status = $1, yookassa_payment_id = $2
                    WHERE id = $3
                    RETURNING id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                """
                result = await fetch_one(query, status, yookassa_payment_id, payment_id)
            else:
                query = """
                    UPDATE payments
                    SET status = $1
                    WHERE id = $2
                    RETURNING id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                """
                result = await fetch_one(query, status, payment_id)
            
            if not result:
                return None
            
            logger.info(f"Обновлен статус платежа {payment_id} на {status}")
            return Payment(**result)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса платежа {payment_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при обновлении статуса платежа: {str(e)}")

    @staticmethod
    async def delete(payment_id: int) -> bool:
        """Удаление платежа."""
        try:
            query = "DELETE FROM payments WHERE id = $1"
            result = await execute_query(query, payment_id)
            
            # Проверяем, была ли удалена хотя бы одна запись
            deleted = "DELETE 1" in result
            
            if deleted:
                logger.info(f"Удален платеж с ID: {payment_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Ошибка при удалении платежа {payment_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при удалении платежа: {str(e)}")

    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> List[Payment]:
        """Получение списка всех платежей с пагинацией."""
        try:
            query = """
                SELECT id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                FROM payments
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            results = await fetch_many(query, limit, offset)
            return [Payment(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка платежей: {str(e)}")
            raise RuntimeError(f"Ошибка при получении списка платежей: {str(e)}")

    @staticmethod
    async def get_total_count() -> int:
        """Получение общего количества платежей."""
        try:
            query = "SELECT COUNT(*) FROM payments"
            result = await fetch_val(query)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества платежей: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества платежей: {str(e)}")

    @staticmethod
    async def get_user_payment_count(user_id: int) -> int:
        """Получение количества платежей пользователя."""
        try:
            query = "SELECT COUNT(*) FROM payments WHERE user_id = $1"
            result = await fetch_val(query, user_id)
            return result or 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества платежей пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении количества платежей: {str(e)}")

    @staticmethod
    async def get_user_total_spent(user_id: int) -> Decimal:
        """Получение общей суммы потраченных средств пользователя."""
        try:
            query = """
                SELECT COALESCE(SUM(amount), 0) 
                FROM payments 
                WHERE user_id = $1 AND status = 'succeeded'
            """
            result = await fetch_val(query, user_id)
            return Decimal(str(result)) if result else Decimal('0')
            
        except Exception as e:
            logger.error(f"Ошибка при получении общей суммы пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении общей суммы: {str(e)}")

    @staticmethod
    async def get_successful_payments_by_user(user_id: int, limit: int = 50, offset: int = 0) -> List[Payment]:
        """Получение успешных платежей пользователя."""
        try:
            query = """
                SELECT id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                FROM payments
                WHERE user_id = $1 AND status = 'succeeded'
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """
            results = await fetch_many(query, user_id, limit, offset)
            return [Payment(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении успешных платежей пользователя {user_id}: {str(e)}")
            raise RuntimeError(f"Ошибка при получении платежей: {str(e)}")

    @staticmethod
    async def get_pending_payments() -> List[Payment]:
        """Получение всех платежей в статусе pending."""
        try:
            query = """
                SELECT id, user_id, yookassa_payment_id, amount, currency, status, description, metadata, created_at, updated_at
                FROM payments
                WHERE status = 'pending'
                ORDER BY created_at ASC
            """
            results = await fetch_many(query)
            return [Payment(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Ошибка при получении ожидающих платежей: {str(e)}")
            raise RuntimeError(f"Ошибка при получении платежей: {str(e)}")