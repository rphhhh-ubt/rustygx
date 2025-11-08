"""Основная точка входа бота."""

import asyncio
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from src.config import settings
from src.handlers import router
from src.locales import messages
from src.services import init_database, close_database

# Настройка логирования
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BotManager:
    """Менеджер для управления ботом."""

    def __init__(self):
        """Инициализация менеджера бота."""
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.app: Optional[web.Application] = None

    async def initialize(self) -> None:
        """Инициализация бота и диспетчера."""
        logger.info("Инициализация бота...")

        # Инициализация базы данных
        await init_database()

        # Создание бота
        self.bot = Bot(token=settings.bot_token)

        # Создание диспетчера
        self.dp = Dispatcher()

        # Регистрация роутеров
        self.dp.include_router(router)

        logger.info(messages.BOT_STARTED)

    async def setup_webhook(self) -> None:
        """Настройка webhook."""
        if not self.bot:
            raise RuntimeError("Бот не инициализирован")

        try:
            # Удаление старого webhook, если он был
            await self.bot.session.delete(
                f"https://api.telegram.org/bot{settings.bot_token}/deleteWebhook"
            )

            # Установка нового webhook
            webhook_info = await self.bot.set_webhook(
                url=f"{settings.webhook_url}{settings.webhook_path}"
            )

            if webhook_info:
                logger.info(
                    messages.WEBHOOK_SET.format(
                        webhook_url=f"{settings.webhook_url}{settings.webhook_path}"
                    )
                )
            else:
                logger.error("Ошибка при установке webhook")

        except Exception as e:
            logger.error(f"Ошибка при настройке webhook: {str(e)}")

    async def start_polling(self) -> None:
        """Запуск бота в режиме polling."""
        if not self.bot or not self.dp:
            raise RuntimeError("Бот не инициализирован")

        try:
            logger.info("Запуск бота в режиме polling...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Ошибка во время polling: {str(e)}")
        finally:
            await self.bot.session.close()

    async def start_webhook_server(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Запуск webhook сервера."""
        if not self.bot or not self.dp:
            raise RuntimeError("Бот не инициализирован")

        try:
            logger.info(f"Запуск webhook сервера на {host}:{port}...")

            # Создание приложения
            self.app = web.Application()

            # Создание обработчика для webhook
            SimpleRequestHandler(
                dispatcher=self.dp,
                bot=self.bot,
            ).register(self.app, path=settings.webhook_path)

            # Настройка приложения
            setup_application(self.app, self.dp, self.bot)

            # Запуск сервера
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()

            logger.info(f"Webhook сервер запущен на http://{host}:{port}")

            # Создание бесконечного цикла для сохранения сервера в работе
            await asyncio.Event().wait()

        except Exception as e:
            logger.error(f"Ошибка при запуске webhook сервера: {str(e)}")

    async def shutdown(self) -> None:
        """Остановка бота."""
        if self.bot:
            await self.bot.session.close()
        
        # Закрытие соединений с базой данных
        await close_database()
        
        logger.info(messages.BOT_STOPPED)


async def main() -> None:
    """Основная функция."""
    bot_manager = BotManager()

    try:
        await bot_manager.initialize()

        # Здесь можно выбрать между polling и webhook
        # Для локальной разработки используйте polling
        # Для production используйте webhook
        await bot_manager.start_polling()

    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
        raise
    finally:
        await bot_manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
