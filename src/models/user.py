"""Модель пользователя."""

from pydantic import BaseModel, Field
from datetime import datetime


class User(BaseModel):
    """Модель данных пользователя."""

    user_id: int = Field(..., description="ID пользователя в Telegram")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")
    username: str | None = Field(None, description="Username в Telegram")
    is_bot: bool = Field(False, description="Является ли пользователь ботом")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Время создания записи")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "user_id": 123456789,
                "first_name": "Иван",
                "last_name": "Петров",
                "username": "ivanov",
                "is_bot": False,
            }
        }
