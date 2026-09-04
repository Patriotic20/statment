from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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
