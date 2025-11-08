"""Модели платежей."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal


class Payment(BaseModel):
    """Модель данных платежа из базы данных."""

    id: int = Field(..., description="ID записи в базе данных")
    user_id: int = Field(..., description="ID пользователя")
    yookassa_payment_id: Optional[str] = Field(None, description="ID платежа в Yookassa")
    amount: Decimal = Field(..., description="Сумма платежа")
    currency: str = Field(..., description="Валюта платежа")
    status: str = Field(..., description="Статус платежа")
    description: Optional[str] = Field(None, description="Описание платежа")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные платежа")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "yookassa_payment_id": "yookassa_12345",
                "amount": "499.00",
                "currency": "RUB",
                "status": "succeeded",
                "description": "Оплата консультации",
                "metadata": {"reading_type": "tarot"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:05:00Z",
            }
        }


class PaymentCreate(BaseModel):
    """Модель для создания платежа."""

    user_id: int = Field(..., description="ID пользователя")
    yookassa_payment_id: Optional[str] = Field(None, description="ID платежа в Yookassa")
    amount: Decimal = Field(..., description="Сумма платежа")
    currency: str = Field("RUB", description="Валюта платежа")
    status: str = Field("pending", description="Статус платежа")
    description: Optional[str] = Field(None, description="Описание платежа")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Метаданные платежа")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "user_id": 1,
                "yookassa_payment_id": "yookassa_12345",
                "amount": "499.00",
                "currency": "RUB",
                "status": "pending",
                "description": "Оплата консультации",
                "metadata": {"reading_type": "tarot"},
            }
        }


class PaymentUpdate(BaseModel):
    """Модель для обновления платежа."""

    yookassa_payment_id: Optional[str] = Field(None, description="ID платежа в Yookassa")
    amount: Optional[Decimal] = Field(None, description="Сумма платежа")
    currency: Optional[str] = Field(None, description="Валюта платежа")
    status: Optional[str] = Field(None, description="Статус платежа")
    description: Optional[str] = Field(None, description="Описание платежа")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные платежа")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "status": "succeeded",
                "yookassa_payment_id": "yookassa_12345",
            }
        }