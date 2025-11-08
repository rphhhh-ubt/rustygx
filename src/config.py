"""Конфигурация приложения."""

from pydantic_settings import BaseSettings
from pydantic import field_validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Параметры конфигурации приложения."""

    # Телеграм
    bot_token: str
    webhook_url: str
    webhook_path: str = "/webhook"
    admin_id: int = 0

    # Базы данных
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    # Yookassa
    yookassa_shop_id: str
    yookassa_api_key: str

    # Приложение
    debug: bool = False
    log_level: str = "INFO"
    webhook_port: int = 8080

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Проверка токена бота."""
        if not v or not v.strip():
            raise ValueError("BOT_TOKEN не может быть пустым. Установите значение в .env файле.")
        if ":" not in v:
            raise ValueError("BOT_TOKEN имеет некорректный формат. Должен быть вида: 123456789:ABCdefGHIjklmnoPQRstuvWXYZ")
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Проверка URL базы данных."""
        if not v or not v.strip():
            raise ValueError("DATABASE_URL не может быть пустым. Установите значение в .env файле.")
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL должен начинаться с 'postgresql://'")
        return v

    @field_validator("yookassa_shop_id", "yookassa_api_key")
    @classmethod
    def validate_yookassa_fields(cls, v: str) -> str:
        """Проверка полей Yookassa."""
        if not v or not v.strip():
            raise ValueError("Параметры Yookassa не могут быть пустыми. Установите значения в .env файле.")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Проверка уровня логирования."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Неверный уровень логирования: {v}. Допустимые значения: {', '.join(valid_levels)}")
        return v.upper()


def get_settings() -> Settings:
    """Получить параметры конфигурации."""
    try:
        return Settings()
    except Exception as e:
        logger.error(f"Ошибка при загрузке конфигурации: {str(e)}")
        raise


settings = get_settings()
