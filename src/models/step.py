"""Модели шагов."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .question import Question


class Step(BaseModel):
    """Модель данных шага из базы данных."""

    id: int = Field(..., description="ID записи в базе данных")
    name: str = Field(..., description="Название шага")
    description: Optional[str] = Field(None, description="Описание шага")
    step_order: int = Field(..., description="Порядковый номер шага")
    is_active: bool = Field(..., description="Флаг активности шага")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Приветствие",
                "description": "Первый шаг - приветствие пользователя",
                "step_order": 1,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class StepCreate(BaseModel):
    """Модель для создания шага."""

    name: str = Field(..., description="Название шага")
    description: Optional[str] = Field(None, description="Описание шага")
    step_order: int = Field(..., description="Порядковый номер шага")
    is_active: bool = Field(True, description="Флаг активности шага")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "name": "Приветствие",
                "description": "Первый шаг - приветствие пользователя",
                "step_order": 1,
                "is_active": True,
            }
        }


class StepUpdate(BaseModel):
    """Модель для обновления шага."""

    name: Optional[str] = Field(None, description="Название шага")
    description: Optional[str] = Field(None, description="Описание шага")
    step_order: Optional[int] = Field(None, description="Порядковый номер шага")
    is_active: Optional[bool] = Field(None, description="Флаг активности шага")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "name": "Приветствие",
                "is_active": False,
            }
        }


class StepWithQuestions(Step):
    """Модель шага с вопросами."""

    questions: List["Question"] = Field(default_factory=list, description="Вопросы шага")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Приветствие",
                "description": "Первый шаг - приветствие пользователя",
                "step_order": 1,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "questions": [
                    {
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
                ],
            }
        }