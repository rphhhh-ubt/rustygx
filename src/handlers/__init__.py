"""Обработчики команд бота."""

from aiogram import Router

from .commands import router as commands_router

# Основной маршрутизатор
router = Router()

# Регистрация всех подмаршрутизаторов
router.include_router(commands_router)
