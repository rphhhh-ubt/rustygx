"""Модели чтений."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class Reading(BaseModel):
    """Модель данных чтения из базы данных."""

    id: int = Field(..., description="ID записи в базе данных")
    user_id: int = Field(..., description="ID пользователя")
    reading_type: str = Field(..., description="Тип чтения")
    reading_payload: Dict[str, Any] = Field(default_factory=dict, description="Данные чтения в формате JSON")
    status: str = Field(..., description="Статус чтения")
    created_at: datetime = Field(..., description="Время создания записи")
    completed_at: Optional[datetime] = Field(None, description="Время завершения чтения")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "reading_type": "tarot",
                "reading_payload": {"cards": ["The Fool", "The Magician"]},
                "status": "completed",
                "created_at": "2024-01-01T00:00:00Z",
                "completed_at": "2024-01-01T01:00:00Z",
            }
        }


class ReadingCreate(BaseModel):
    """Модель для создания чтения."""

    user_id: int = Field(..., description="ID пользователя")
    reading_type: str = Field(..., description="Тип чтения")
    reading_payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Данные чтения в формате JSON")
    status: str = Field("pending", description="Статус чтения")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "user_id": 1,
                "reading_type": "tarot",
                "reading_payload": {"cards": ["The Fool", "The Magician"]},
                "status": "pending",
            }
        }


class ReadingUpdate(BaseModel):
    """Модель для обновления чтения."""

    reading_type: Optional[str] = Field(None, description="Тип чтения")
    reading_payload: Optional[Dict[str, Any]] = Field(None, description="Данные чтения в формате JSON")
    status: Optional[str] = Field(None, description="Статус чтения")
    completed_at: Optional[datetime] = Field(None, description="Время завершения чтения")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "reading_type": "tarot",
                "reading_payload": {"cards": ["The Fool", "The Magician"]},
                "status": "completed",
                "completed_at": "2024-01-01T01:00:00Z",
            }
        }