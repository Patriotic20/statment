from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def issue_actions_keyboard(issue_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Ishga olish",
                callback_data=f"accept:{issue_id}",
            ),
            InlineKeyboardButton(
                text="🔒 Yakunlash",
                callback_data=f"resolve:{issue_id}",
            ),
        ]
    ])
