"""Модели пользователей."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class User(BaseModel):
    """Модель данных пользователя из базы данных."""

    id: int = Field(..., description="ID записи в базе данных")
    telegram_id: int = Field(..., description="ID пользователя в Telegram")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Username в Telegram")
    is_bot: bool = Field(False, description="Является ли пользователь ботом")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "telegram_id": 123456789,
                "first_name": "Иван",
                "last_name": "Петров",
                "username": "ivanov",
                "is_bot": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class UserCreate(BaseModel):
    """Модель для создания пользователя."""

    telegram_id: int = Field(..., description="ID пользователя в Telegram")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Username в Telegram")
    is_bot: bool = Field(False, description="Является ли пользователь ботом")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "first_name": "Иван",
                "last_name": "Петров",
                "username": "ivanov",
                "is_bot": False,
            }
        }


class UserUpdate(BaseModel):
    """Модель для обновления пользователя."""

    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Username в Telegram")
    is_bot: Optional[bool] = Field(None, description="Является ли пользователь ботом")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "first_name": "Иван",
                "last_name": "Петров",
                "username": "ivanov",
                "is_bot": False,
            }
        }
