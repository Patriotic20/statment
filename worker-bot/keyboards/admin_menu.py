from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
    ReplyKeyboardMarkup, WebAppInfo,
)

from config import settings

BTN_ROOM = "🏢 Xona"
BTN_EMPLOYEE = "👤 Xodim"
BTN_INVENTORY = "🖥 Uskuna"
BTN_ASSIGN = "🔗 Uskunani biriktirish"


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Меню воркера. Показывается после успешной авторизации."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ROOM), KeyboardButton(text=BTN_EMPLOYEE)],
            [KeyboardButton(text=BTN_INVENTORY)],
            [KeyboardButton(text=BTN_ASSIGN)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Nima qo'shamiz?",
    )


def miniapp_keyboard() -> InlineKeyboardMarkup | None:
    """Кнопка открытия Mini App. None, если адрес не задан (локальный запуск)."""
    if not settings.miniapp_url:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📱 Ilovani ochish",
            web_app=WebAppInfo(url=settings.miniapp_url),
        )
    ]])
