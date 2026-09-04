"""Инлайн-клавиатуры для шагов мастеров: списки с пагинацией и кнопки шага.

callback_data устроены как `<kind>:<value>`; префиксы не пересекаются с
`accept:`/`resolve:` из уведомлений о заявках.
"""
from typing import Any, Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

PAGE_SIZE = 6

CB_CANCEL = "wiz_cancel"
CB_SKIP = "wiz_skip"


def _nav_row(kind: str, offset: int, total: int) -> list[InlineKeyboardButton]:
    row: list[InlineKeyboardButton] = []
    if offset > 0:
        row.append(InlineKeyboardButton(
            text="◀️", callback_data=f"page:{kind}:{max(offset - PAGE_SIZE, 0)}"
        ))
    if offset + PAGE_SIZE < total:
        row.append(InlineKeyboardButton(
            text="▶️", callback_data=f"page:{kind}:{offset + PAGE_SIZE}"
        ))
    return row


def picker_keyboard(
    kind: str,
    items: Sequence[dict[str, Any]],
    label_key: str = "name",
    offset: int = 0,
    extra_rows: Sequence[Sequence[InlineKeyboardButton]] = (),
) -> InlineKeyboardMarkup:
    """Список для выбора: kind задаёт префикс callback — `pick:<kind>:<id>`."""
    page = items[offset:offset + PAGE_SIZE]
    rows = [
        [InlineKeyboardButton(
            text=str(item.get(label_key, item["id"]))[:60],
            callback_data=f"pick:{kind}:{item['id']}",
        )]
        for item in page
    ]
    nav = _nav_row(kind, offset, len(items))
    if nav:
        rows.append(nav)
    rows.extend([list(row) for row in extra_rows])
    rows.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data=CB_CANCEL)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def floor_keyboard() -> InlineKeyboardMarkup:
    """Этажи 1–4 — ровно те значения, что допускает enum Floor на бэкенде."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(n), callback_data=f"pick:floor:{n}") for n in (1, 2, 3, 4)],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=CB_CANCEL)],
    ])


def device_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💻 Kompyuter", callback_data="pick:device:computer")],
        [InlineKeyboardButton(text="🖨 Printer", callback_data="pick:device:printer")],
        [InlineKeyboardButton(text="🌐 Tarmoq qurilmasi", callback_data="pick:device:network")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=CB_CANCEL)],
    ])


def skip_keyboard() -> InlineKeyboardMarkup:
    """Для необязательных шагов: фото, IP, MAC."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data=CB_SKIP)],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=CB_CANCEL)],
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=CB_CANCEL)],
    ])


def new_employee_row() -> list[InlineKeyboardButton]:
    """Кнопка «создать сотрудника прямо здесь» для мастера оборудования."""
    return [InlineKeyboardButton(text="➕ Yangi xodim qo'shish", callback_data="wiz_new_employee")]
