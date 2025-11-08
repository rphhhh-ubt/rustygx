"""Модели вопросов."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class Question(BaseModel):
    """Модель данных вопроса из базы данных."""

    id: int = Field(..., description="ID записи в базе данных")
    step_id: int = Field(..., description="ID шага")
    question_text: str = Field(..., description="Текст вопроса")
    question_type: str = Field(..., description="Тип вопроса")
    options: List[Dict[str, Any]] = Field(default_factory=list, description="Варианты ответов")
    question_order: int = Field(..., description="Порядковый номер вопроса")
    is_required: bool = Field(..., description="Обязателен ли ответ")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "step_id": 1,
                "question_text": "Как вас зовут?",
                "question_type": "text",
                "options": [],
                "question_order": 1,
                "is_required": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class QuestionCreate(BaseModel):
    """Модель для создания вопроса."""

    step_id: int = Field(..., description="ID шага")
    question_text: str = Field(..., description="Текст вопроса")
    question_type: str = Field("text", description="Тип вопроса")
    options: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Варианты ответов")
    question_order: int = Field(..., description="Порядковый номер вопроса")
    is_required: bool = Field(True, description="Обязателен ли ответ")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "step_id": 1,
                "question_text": "Как вас зовут?",
                "question_type": "text",
                "options": [],
                "question_order": 1,
                "is_required": True,
            }
        }


class QuestionUpdate(BaseModel):
    """Модель для обновления вопроса."""

    question_text: Optional[str] = Field(None, description="Текст вопроса")
    question_type: Optional[str] = Field(None, description="Тип вопроса")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="Варианты ответов")
    question_order: Optional[int] = Field(None, description="Порядковый номер вопроса")
    is_required: Optional[bool] = Field(None, description="Обязателен ли ответ")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "question_text": "Как ваше имя?",
                "is_required": False,
            }
        }