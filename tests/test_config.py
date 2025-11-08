"""Базовые тесты для Telegram бота."""

import pytest
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Settings, get_settings


class TestConfig:
    """Тесты конфигурации."""
    
    def test_settings_creation(self):
        """Тест создания настроек с минимальными параметрами."""
        settings = Settings(
            bot_token="123456:ABC-DEF",
            database_url="postgresql://user:pass@localhost:5432/test",
            yookassa_shop_id="test_shop",
            yookassa_api_key="test_key"
        )
        assert settings.bot_token == "123456:ABC-DEF"
        assert settings.webhook_path == "/webhook"
        assert settings.admin_id == 0
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.webhook_port == 8080
    
    def test_bot_token_validation(self):
        """Тест валидации токена бота."""
        with pytest.raises(ValueError, match="BOT_TOKEN не может быть пустым"):
            Settings(
                bot_token="",
                database_url="postgresql://user:pass@localhost:5432/test",
                yookassa_shop_id="test_shop",
                yookassa_api_key="test_key"
            )
        
        with pytest.raises(ValueError, match="BOT_TOKEN имеет некорректный формат"):
            Settings(
                bot_token="invalid_token",
                database_url="postgresql://user:pass@localhost:5432/test",
                yookassa_shop_id="test_shop",
                yookassa_api_key="test_key"
            )
    
    def test_database_url_validation(self):
        """Тест валидации URL базы данных."""
        with pytest.raises(ValueError, match="DATABASE_URL должен начинаться с"):
            Settings(
                bot_token="123456:ABC-DEF",
                database_url="mysql://user:pass@localhost:5432/test",
                yookassa_shop_id="test_shop",
                yookassa_api_key="test_key"
            )
    
    def test_log_level_validation(self):
        """Тест валидации уровня логирования."""
        settings = Settings(
            bot_token="123456:ABC-DEF",
            database_url="postgresql://user:pass@localhost:5432/test",
            yookassa_shop_id="test_shop",
            yookassa_api_key="test_key",
            log_level="debug"
        )
        assert settings.log_level == "DEBUG"
        
        with pytest.raises(ValueError, match="Неверный уровень логирования"):
            Settings(
                bot_token="123456:ABC-DEF",
                database_url="postgresql://user:pass@localhost:5432/test",
                yookassa_shop_id="test_shop",
                yookassa_api_key="test_key",
                log_level="INVALID"
            )


if __name__ == "__main__":
    pytest.main([__file__])