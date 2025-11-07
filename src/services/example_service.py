"""Пример сервиса."""

import logging

logger = logging.getLogger(__name__)


class ExampleService:
    """Пример класса сервиса для бизнес-логики."""

    @staticmethod
    async def get_data() -> dict:
        """Пример метода для получения данных."""
        logger.info("Получение данных из сервиса")
        return {"status": "ok", "data": "Пример данных"}

    @staticmethod
    async def process_data(data: dict) -> dict:
        """Пример метода для обработки данных."""
        logger.info(f"Обработка данных: {data}")
        return {"status": "processed", "data": data}
