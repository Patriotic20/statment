from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_issue_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💻 Kompyuter")],
            [KeyboardButton(text="🌐 Tarmoq")],
            [KeyboardButton(text="🖨 Printer")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Muammoni tanlang..."
    )
    return keyboard
