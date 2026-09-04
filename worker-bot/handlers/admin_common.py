"""Общие элементы мастеров: авторизация, отмена, пагинация, вывод ошибок."""
import logging
from typing import Any, Awaitable, Callable, Sequence

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message

import api_client
from api_client import ApiError
from keyboards.admin_menu import admin_menu_keyboard
from keyboards.pickers import CB_CANCEL, picker_keyboard

logger = logging.getLogger(__name__)

router = Router()


async def ensure_authorized(message: Message) -> bool:
    """Мастера доступны только авторизованным воркерам — у них есть токен."""
    if api_client.get_token(message.from_user.id) is not None:
        return True
    await message.answer(
        "Сначала авторизуйтесь: отправьте /start и введите логин и пароль."
    )
    return False


async def run_api(message: Message, action: Awaitable[Any]) -> tuple[bool, Any]:
    """Выполняет запрос к бэкенду, показывая причину отказа прямо в чате."""
    try:
        return True, await action
    except ApiError as exc:
        await message.answer(f"❌ {exc.message}")
        return False, None
    except Exception as exc:  # сеть, таймаут и прочее
        logger.exception("Не удалось выполнить запрос к API")
        await message.answer(f"❌ Не удалось связаться с сервером: {exc}")
        return False, None


async def send_picker(
    message: Message,
    state: FSMContext,
    kind: str,
    items: Sequence[dict[str, Any]],
    prompt: str,
    empty_text: str,
    label_key: str = "name",
    extra_rows: Sequence[Sequence[InlineKeyboardButton]] = (),
) -> bool:
    """Показывает список для выбора и запоминает его для пагинации."""
    if not items:
        # Пустой empty_text — вызывающий сам решит, что показать (Telegram не
        # принимает сообщения без текста).
        if empty_text:
            await message.answer(empty_text)
        return False
    await state.update_data(
        pick_items=list(items), pick_kind=kind, pick_label=label_key,
        pick_extra=[[btn.model_dump(exclude_none=True) for btn in row] for row in extra_rows],
    )
    await message.answer(
        prompt,
        reply_markup=picker_keyboard(kind, items, label_key=label_key, extra_rows=extra_rows),
    )
    return True


@router.callback_query(F.data.startswith("page:"))
async def paginate(callback: CallbackQuery, state: FSMContext):
    """Листает любой список мастера — данные лежат в state после send_picker."""
    _, kind, raw_offset = callback.data.split(":")
    data = await state.get_data()
    items = data.get("pick_items") or []
    if not items:
        await callback.answer("Список устарел, начните шаг заново", show_alert=True)
        return
    extra_rows = [
        [InlineKeyboardButton(**btn) for btn in row] for row in data.get("pick_extra", [])
    ]
    await callback.message.edit_reply_markup(
        reply_markup=picker_keyboard(
            kind, items,
            label_key=data.get("pick_label", "name"),
            offset=int(raw_offset),
            extra_rows=extra_rows,
        )
    )
    await callback.answer()


@router.callback_query(F.data == CB_CANCEL)
async def cancel_wizard(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Отменено.", reply_markup=admin_menu_keyboard())
    await callback.answer()
