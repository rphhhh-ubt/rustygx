"""Сервис для работы с платежами YooKassa."""

import logging
import hmac
import hashlib
from typing import Optional, Dict, Any
from decimal import Decimal

from aiohttp import web
from yookassa import Configuration, Payment as YooKassaPayment
from yookassa.domain.common import SecurityHelper
from yookassa.domain.response import PaymentResponse

from ..config import settings
from ..models.payment import PaymentCreate, PaymentUpdate
from ..services.payment_repository import PaymentRepository
from ..services.user_repository import UserRepository
from ..locales import messages

logger = logging.getLogger(__name__)


class PaymentService:
    """Сервис для работы с платежами."""

    def __init__(self):
        """Инициализация сервиса."""
        # Настройка YooKassa
        Configuration.account_id = settings.yookassa_shop_id
        Configuration.secret_key = settings.yookassa_api_key

        # Цены пакетов чтений (в рублях)
        self.PACKAGES = {
            "buy_5": {
                "readings": 5,
                "amount": Decimal("299.00"),
                "description": "Пакет из 5 платных чтений"
            },
            "buy_10": {
                "readings": 10,
                "amount": Decimal("499.00"),
                "description": "Пакет из 10 платных чтений"
            },
            "buy_20": {
                "readings": 20,
                "amount": Decimal("899.00"),
                "description": "Пакет из 20 платных чтений"
            }
        }

    async def create_payment(self, user_id: int, package_type: str) -> Optional[Dict[str, Any]]:
        """Создание платежа в YooKassa и запись в БД.
        
        Args:
            user_id: ID пользователя в БД
            package_type: Тип пакета (buy_5, buy_10, buy_20)
            
        Returns:
            Словарь с payment_id и confirmation_url или None при ошибке
        """
        try:
            # Проверяем существование пакета
            if package_type not in self.PACKAGES:
                logger.error(f"Неизвестный тип пакета: {package_type}")
                return None

            package = self.PACKAGES[package_type]
            
            # Создаем платеж в YooKassa
            yookassa_payment = YooKassaPayment.create({
                "amount": {
                    "value": str(package["amount"]),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"https://t.me/{settings.bot_token.split(':')[0]}"
                },
                "capture": True,
                "description": package["description"],
                "metadata": {
                    "user_id": str(user_id),
                    "package_type": package_type,
                    "readings": str(package["readings"])
                }
            })

            # Сохраняем платеж в БД
            payment_data = PaymentCreate(
                user_id=user_id,
                yookassa_payment_id=yookassa_payment.id,
                amount=package["amount"],
                currency="RUB",
                status="pending",
                description=package["description"],
                metadata={
                    "package_type": package_type,
                    "readings": package["readings"]
                }
            )

            payment = await PaymentRepository.create(payment_data)
            
            logger.info(f"Создан платеж {payment.id} для пользователя {user_id} на сумму {package['amount']}")
            
            return {
                "payment_id": payment.id,
                "yookassa_payment_id": yookassa_payment.id,
                "confirmation_url": yookassa_payment.confirmation.confirmation_url,
                "amount": str(package["amount"]),
                "description": package["description"]
            }

        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {str(e)}")
            return None

    async def check_payment_status(self, yookassa_payment_id: str) -> Optional[str]:
        """Проверка статуса платежа в YooKassa.
        
        Args:
            yookassa_payment_id: ID платежа в YooKassa
            
        Returns:
            Статус платежа или None при ошибке
        """
        try:
            payment = YooKassaPayment.find_one(yookassa_payment_id)
            return payment.status
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса платежа {yookassa_payment_id}: {str(e)}")
            return None

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Проверка подписи webhook от YooKassa.
        
        Args:
            payload: Тело запроса
            signature: Подпись из заголовка
            
        Returns:
            True если подпись верна, иначе False
        """
        try:
            # Создаем HMAC-SHA256 хеш
            expected_signature = hmac.new(
                settings.yookassa_api_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # YooKassa присылает подпись в формате "sha256_hash"
            received_signature = signature.replace('sha256_', '')
            
            return hmac.compare_digest(expected_signature, received_signature)
        except Exception as e:
            logger.error(f"Ошибка при проверке подписи webhook: {str(e)}")
            return False

    async def handle_webhook(self, request_data: Dict[str, Any]) -> bool:
        """Обработка webhook от YooKassa.
        
        Args:
            request_data: Данные webhook
            
        Returns:
            True если обработка успешна, иначе False
        """
        try:
            # Проверяем тип события
            event = request_data.get('event')
            if event != 'payment.succeeded':
                logger.info(f"Пропускаем событие: {event}")
                return True

            payment_object = request_data.get('object', {})
            yookassa_payment_id = payment_object.get('id')
            
            if not yookassa_payment_id:
                logger.error("Отсутствует ID платежа в webhook")
                return False

            # Ищем платеж в БД
            payment = await PaymentRepository.get_by_yookassa_id(yookassa_payment_id)
            
            if not payment:
                logger.error(f"Платеж {yookassa_payment_id} не найден в БД")
                return False

            # Проверяем статус для идемпотентности
            if payment.status == 'succeeded':
                logger.info(f"Платеж {payment.id} уже обработан")
                return True

            # Обновляем статус платежа
            updated_payment = await PaymentRepository.update_status(
                payment.id, 
                'succeeded',
                yookassa_payment_id
            )

            if not updated_payment:
                logger.error(f"Не удалось обновить статус платежа {payment.id}")
                return False

            # Начисляем чтения пользователю
            metadata = payment.metadata
            package_type = metadata.get('package_type')
            readings_count = int(metadata.get('readings', 0))

            if readings_count > 0:
                # Здесь должна быть логика обновления баланса пользователя
                # Поскольку в текущей модели пользователя нет полей баланса,
                # мы просто логируем начисление
                logger.info(f"Начислено {readings_count} чтений пользователю {payment.user_id}")
                
                # TODO: Реализовать обновление баланса в модели пользователя
                # await self._add_paid_readings_to_user(payment.user_id, readings_count)

            logger.info(f"Платеж {payment.id} успешно обработан")
            return True

        except Exception as e:
            logger.error(f"Ошибка при обработке webhook: {str(e)}")
            return False

    async def get_user_payments(self, user_id: int) -> list:
        """Получение платежей пользователя.
        
        Args:
            user_id: ID пользователя в БД
            
        Returns:
            Список платежей пользователя
        """
        try:
            return await PaymentRepository.get_by_user_id(user_id)
        except Exception as e:
            logger.error(f"Ошибка при получении платежей пользователя {user_id}: {str(e)}")
            return []

    def get_package_info(self, package_type: str) -> Optional[Dict[str, Any]]:
        """Получение информации о пакете.
        
        Args:
            package_type: Тип пакета
            
        Returns:
            Информация о пакете или None
        """
        return self.PACKAGES.get(package_type)

    async def _add_paid_readings_to_user(self, user_id: int, readings_count: int) -> bool:
        """Добавление платных чтений пользователю.
        
        Args:
            user_id: ID пользователя в БД
            readings_count: Количество чтений для начисления
            
        Returns:
            True если успешно, иначе False
        """
        # TODO: Реализовать после добавления полей баланса в модель пользователя
        # Эта функция должна обновлять поле paid_readings_left в таблице users
        logger.info(f"TODO: Добавить {readings_count} платных чтений пользователю {user_id}")
        return True


# Создание экземпляра сервиса
payment_service = PaymentService()


async def yookassa_webhook_handler(request: web.Request) -> web.Response:
    """Обработчик webhook для YooKassa.
    
    Args:
        request: HTTP запрос
        
    Returns:
        HTTP ответ
    """
    try:
        # Получаем подпись из заголовка
        signature = request.headers.get('HTTP_YOOKASSA_SIGNATURE') or request.headers.get('Yookassa-Signature')
        
        if not signature:
            logger.warning("Отсутствует подпись webhook")
            return web.Response(status=400, text="Missing signature")

        # Получаем тело запроса
        payload = await request.text()
        
        # Проверяем подпись
        if not payment_service.verify_webhook_signature(payload, signature):
            logger.warning("Неверная подпись webhook")
            return web.Response(status=401, text="Invalid signature")

        # Парсим JSON
        import json
        request_data = json.loads(payload)

        # Обрабатываем webhook
        success = await payment_service.handle_webhook(request_data)
        
        if success:
            return web.Response(status=200, text="OK")
        else:
            return web.Response(status=500, text="Processing error")

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON webhook: {str(e)}")
        return web.Response(status=400, text="Invalid JSON")
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {str(e)}")
        return web.Response(status=500, text="Internal server error")