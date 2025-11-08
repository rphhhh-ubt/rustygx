"""Обработчики платежных команд."""

import logging
from typing import Dict, Any

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..config import settings
from ..services.payments import payment_service
from ..services.user_repository import UserRepository
from ..locales import messages

logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()


def create_payment_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с вариантами покупки."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💎 5 чтений - 299₽",
                callback_data="buy_5"
            )
        ],
        [
            InlineKeyboardButton(
                text="💎💎 10 чтений - 499₽", 
                callback_data="buy_10"
            )
        ],
        [
            InlineKeyboardButton(
                text="💎💎💎 20 чтений - 899₽",
                callback_data="buy_20"
            )
        ],
        [
            InlineKeyboardButton(
                text=messages.BUTTON_BACK_TO_MENU,
                callback_data="back_to_menu"
            )
        ]
    ])
    return keyboard


@router.callback_query(F.data.startswith("buy_"))
async def handle_buy_callback(callback: CallbackQuery, bot: Bot) -> None:
    """Обработчик нажатия на кнопки покупки."""
    try:
        package_type = callback.data
        user_telegram_id = callback.from_user.id
        
        # Получаем пользователя из БД
        user = await UserRepository.get_by_telegram_id(user_telegram_id)
        if not user:
            await callback.answer(
                messages.PAYMENT_USER_NOT_FOUND,
                show_alert=True
            )
            return

        # Получаем информацию о пакете
        package_info = payment_service.get_package_info(package_type)
        if not package_info:
            await callback.answer(
                messages.PAYMENT_PACKAGE_NOT_FOUND,
                show_alert=True
            )
            return

        # Создаем платеж
        payment_result = await payment_service.create_payment(user.id, package_type)
        
        if not payment_result:
            await callback.answer(
                messages.PAYMENT_CREATION_ERROR,
                show_alert=True
            )
            return

        # Отправляем сообщение с кнопкой оплаты
        payment_text = messages.PAYMENT_DETAILS.format(
            package=package_info['description'],
            amount=payment_result['amount'],
            payment_id=payment_result['payment_id']
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=messages.BUTTON_PAY,
                    url=payment_result['confirmation_url']
                )
            ],
            [
                InlineKeyboardButton(
                    text=messages.BUTTON_BACK_TO_MENU,
                    callback_data="back_to_menu"
                )
            ]
        ])

        await bot.send_message(
            callback.message.chat.id,
            payment_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

        # Подтверждаем обработку callback
        await callback.answer()

        logger.info(f"Создан платеж {payment_result['payment_id']} для пользователя {user.id}")

    except Exception as e:
        logger.error(f"Ошибка при обработке покупки: {str(e)}")
        await callback.answer(
            messages.PAYMENT_CREATION_ERROR,
            show_alert=True
        )


@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery) -> None:
    """Обработчик возврата в меню."""
    try:
        await callback.answer()
        # Здесь можно показать главное меню
        await callback.message.edit_text(
            "📋 Вы вернулись в главное меню.\n\nИспользуйте команды:\n/start - Начать\n/buy - Купить чтения",
            reply_markup=None
        )
    except Exception as e:
        logger.error(f"Ошибка при возврате в меню: {str(e)}")


@router.message(Command("buy"))
async def handle_buy_command(message: Message) -> None:
    """Обработчик команды /buy."""
    try:
        # Получаем пользователя из БД
        user = await UserRepository.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer(
                messages.PAYMENT_USER_NOT_FOUND
            )
            return

        # Показываем меню покупки
        keyboard = create_payment_keyboard()

        await message.answer(
            messages.PAYMENT_COMMAND_TEXT,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке команды /buy: {str(e)}")
        await message.answer(
            messages.PAYMENT_CREATION_ERROR
        )


@router.message(Command("payments"))
async def handle_payments_command(message: Message) -> None:
    """Обработчик команды /payments - история платежей."""
    try:
        # Получаем пользователя из БД
        user = await UserRepository.get_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer(
                messages.PAYMENT_USER_NOT_FOUND
            )
            return

        # Получаем платежи пользователя
        payments = await payment_service.get_user_payments(user.id)
        
        if not payments:
            await message.answer(messages.PAYMENT_HISTORY_EMPTY)
            return

        # Формируем сообщение с историей платежей
        payments_text = f"{messages.PAYMENT_HISTORY_TITLE}\n\n"
        
        for payment in payments[-10:]:  # Показываем последние 10 платежей
            status_emoji = {
                "pending": "⏳",
                "succeeded": "✅", 
                "canceled": "❌",
                "failed": "❌"
            }.get(payment.status, "❓")
            
            payments_text += f"{status_emoji} **#{payment.id}** - {payment.amount} {payment.currency}\n"
            payments_text += f"📅 {payment.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            payments_text += f"📝 {payment.description or 'Без описания'}\n"
            payments_text += f"🔹 Статус: {payment.status}\n\n"

        await message.answer(
            payments_text,
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке команды /payments: {str(e)}")
        await message.answer(
            messages.PAYMENT_HISTORY_ERROR
        )