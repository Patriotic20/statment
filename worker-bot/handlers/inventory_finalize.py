"""Финальный шаг мастера оборудования: создание записи и загрузка фото.

Вынесено отдельным модулем, потому что вызывается из двух мест: из самого
мастера оборудования и из мастера сотрудника, когда владельца создают по ходу.
"""
import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import api_client
from handlers.admin_common import run_api
from keyboards.admin_menu import admin_menu_keyboard

logger = logging.getLogger(__name__)

DEVICE_LABELS = {
    "computer": "💻 Kompyuter",
    "printer": "🖨 Printer",
    "network": "🌐 Tarmoq qurilmasi",
}


async def _attach_photo(message: Message, telegram_id: int, inventory_id: int, draft: dict) -> str:
    """Скачивает фото из Telegram и отправляет его бэкенду.

    Возвращает строку для итогового сообщения. Запись об оборудовании к этому
    моменту уже создана, поэтому ошибка загрузки не отменяет её — сообщаем и
    предлагаем добавить фото позже.
    """
    file_id = draft.get("photo_file_id")
    if not file_id:
        return "rasmsiz"

    try:
        file = await message.bot.get_file(file_id)
        buffer = await message.bot.download_file(file.file_path)
        content = buffer.read()
        mime = draft.get("photo_mime") or "image/jpeg"
        extension = {"image/png": "png", "image/webp": "webp"}.get(mime, "jpg")
        await api_client.upload_inventory_photo(
            telegram_id, inventory_id, content, f"photo.{extension}", mime
        )
        return "rasm yuklandi"
    except Exception as exc:
        logger.warning("Не удалось загрузить фото для inventory %s: %s", inventory_id, exc)
        return f"⚠️ rasm yuklanmadi ({exc}) — keyinroq veb-panelda qo'shish mumkin"


async def finalize_inventory(
    message: Message, state: FSMContext, telegram_id: int, employee_id: int
) -> None:
    """Создаёт оборудование из черновика в state и привязывает его к сотруднику."""
    data = await state.get_data()
    payload = {
        "name": data["inv_name"],
        "employee_id": employee_id,
        "device_type": data.get("inv_device_type"),
        "ip_address": data.get("inv_ip"),
        "mac_address": data.get("inv_mac"),
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    ok, item = await run_api(message, api_client.create_inventory(telegram_id, payload))
    if not ok:
        # Черновик оставляем: пользователь может исправить данные и повторить.
        return

    photo_note = await _attach_photo(message, telegram_id, item["id"], data)
    await state.clear()

    lines = [f"✅ «{item['name']}» uskunasi qo'shildi (id {item['id']}, {photo_note})."]
    if item.get("device_type"):
        lines.append(f"Turi: {DEVICE_LABELS.get(item['device_type'], item['device_type'])}")
    if item.get("ip_address"):
        lines.append(f"IP: {item['ip_address']}")
    if item.get("mac_address"):
        lines.append(f"MAC: {item['mac_address']}")
    await message.answer("\n".join(lines), reply_markup=admin_menu_keyboard())
