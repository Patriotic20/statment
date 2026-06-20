from aiogram import Router, F
from aiogram.types import Message

import api_client

router = Router()

# Соответствие кнопки клавиатуры типу заявки в backend.
ISSUE_TYPES = {
    "💻 Computer issue": "computer",
    "🌐 Network issue": "network",
    "🖨 Printer issue": "printer",
}


@router.message(F.text.in_(ISSUE_TYPES))
async def handle_issue(message: Message):
    issue_type = ISSUE_TYPES[message.text]
    ok, error = await api_client.create_issue(message.from_user.id, issue_type)
    if ok:
        await message.answer("✅ Ваша заявка принята. Специалист скоро свяжется с вами.")
    elif error:
        # Конкретная причина от backend (нет устройства / уже есть открытая заявка и т.п.)
        await message.answer(f"❌ {error}")
    else:
        await message.answer(
            "❌ Не удалось отправить заявку. "
            "Возможно, вы не идентифицированы — отправьте /start."
        )
