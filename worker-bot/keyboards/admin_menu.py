from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BTN_ROOM = "🏢 Кабинет"
BTN_EMPLOYEE = "👤 Сотрудник"
BTN_INVENTORY = "🖥 Оборудование"
BTN_ASSIGN = "🔗 Назначить оборудование"


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Меню воркера. Показывается после успешной авторизации."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ROOM), KeyboardButton(text=BTN_EMPLOYEE)],
            [KeyboardButton(text=BTN_INVENTORY)],
            [KeyboardButton(text=BTN_ASSIGN)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Что добавляем?",
    )
