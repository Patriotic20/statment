from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import api_client
from keyboards.main_menu import get_issue_keyboard
from states import AuthStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик базовой команды /start.

    Если клиент уже привязан по ЖШИР — показываем меню выбора проблемы.
    Иначе просим ввести ЖШИР для идентификации.
    """
    client = await api_client.get_client(message.from_user.id)
    if client is not None:
        await state.clear()
        await message.answer(
            f"Здравствуйте, {message.from_user.first_name}! 👋\n\n"
            "Пожалуйста, выберите с чем у вас возникла проблема:",
            reply_markup=get_issue_keyboard(),
        )
        return

    await state.set_state(AuthStates.waiting_for_jshir)
    await message.answer(
        f"Здравствуйте, {message.from_user.first_name}! 👋\n\n"
        "Для начала введите ваш ЖШИР (14 цифр):"
    )


@router.message(AuthStates.waiting_for_jshir, F.text)
async def process_jshir(message: Message, state: FSMContext):
    """Принимает ЖШИР, проверяет его в backend и привязывает клиента."""
    ok, error = await api_client.link_client(
        telegram_id=message.from_user.id,
        jshir=message.text,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    if not ok:
        await message.answer(f"❌ {error}\n\nПожалуйста, введите корректный ЖШИР ещё раз:")
        return

    await state.clear()
    await message.answer(
        "✅ Вы успешно идентифицированы.\n\n"
        "Пожалуйста, выберите с чем у вас возникла проблема:",
        reply_markup=get_issue_keyboard(),
    )
