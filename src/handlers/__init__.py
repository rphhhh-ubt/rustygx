"""Обработчики команд бота."""

from aiogram import Router

from .commands import router as commands_router
from .scenarios import router as scenarios_router
from .admin import router as admin_router

# Основной маршрутизатор
router = Router()

# Регистрация всех подмаршрутизаторов
router.include_router(commands_router)
router.include_router(scenarios_router)
router.include_router(admin_router)
