from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_issue_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💻 Computer issue")],
            [KeyboardButton(text="🌐 Network issue")],
            [KeyboardButton(text="🖨 Printer issue")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Select an issue..."
    )
    return keyboard
