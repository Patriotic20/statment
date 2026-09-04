"""Мастер добавления оборудования и назначение его сотруднику.

Порядок: название → тип → фото → IP → MAC → факультет → кабинет → сотрудник.
Владелец обязателен (inventory.employee_id NOT NULL), поэтому сотрудник — часть
мастера; если нужного нет, его можно создать не выходя из процесса.
"""
import ipaddress
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import api_client
from handlers.admin_common import ensure_authorized, run_api, send_picker
from handlers.admin_employees import begin_employee_wizard
from handlers.inventory_finalize import DEVICE_LABELS, finalize_inventory
from keyboards.admin_menu import BTN_ASSIGN, BTN_INVENTORY, admin_menu_keyboard
from keyboards.pickers import (
    CB_SKIP, cancel_keyboard, device_type_keyboard, new_employee_row, skip_keyboard,
)
from states import AssignStates, InventoryStates

logger = logging.getLogger(__name__)

router = Router()


# ── Мастер добавления оборудования ───────────────────────────────────────────

@router.message(F.text == BTN_INVENTORY)
async def start_inventory_wizard(message: Message, state: FSMContext):
    if not await ensure_authorized(message):
        return
    await state.clear()
    await state.set_state(InventoryStates.waiting_name)
    await message.answer(
        "Название оборудования (например, «Dell Optiplex 7090»):",
        reply_markup=cancel_keyboard(),
    )


@router.message(InventoryStates.waiting_name, F.text)
async def inventory_name(message: Message, state: FSMContext):
    await state.update_data(inv_name=message.text.strip())
    await state.set_state(InventoryStates.waiting_device_type)
    await message.answer("Тип устройства:", reply_markup=device_type_keyboard())


@router.callback_query(InventoryStates.waiting_device_type, F.data.startswith("pick:device:"))
async def inventory_device_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(inv_device_type=callback.data.split(":")[2])
    await callback.answer()
    await state.set_state(InventoryStates.waiting_photo)
    await callback.message.answer(
        "Пришлите фотографию устройства (снимок или файл-изображение):",
        reply_markup=skip_keyboard(),
    )


@router.message(InventoryStates.waiting_photo, F.photo)
async def inventory_photo(message: Message, state: FSMContext):
    # Берём самый крупный из предложенных Telegram размеров.
    await state.update_data(
        photo_file_id=message.photo[-1].file_id, photo_mime="image/jpeg"
    )
    await _ask_ip(message, state)


@router.message(InventoryStates.waiting_photo, F.document)
async def inventory_photo_as_file(message: Message, state: FSMContext):
    """Фото, отправленное «без сжатия», приходит документом."""
    mime = message.document.mime_type or ""
    if mime not in {"image/jpeg", "image/png", "image/webp"}:
        await message.answer(
            "Нужен файл-изображение (JPEG, PNG или WebP). Пришлите фото ещё раз "
            "или нажмите «Пропустить».",
            reply_markup=skip_keyboard(),
        )
        return
    await state.update_data(photo_file_id=message.document.file_id, photo_mime=mime)
    await _ask_ip(message, state)


@router.callback_query(InventoryStates.waiting_photo, F.data == CB_SKIP)
async def inventory_photo_skip(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await _ask_ip(callback.message, state)


async def _ask_ip(message: Message, state: FSMContext) -> None:
    await state.set_state(InventoryStates.waiting_ip)
    await message.answer(
        "IP-адрес устройства, если есть:", reply_markup=skip_keyboard()
    )


@router.message(InventoryStates.waiting_ip, F.text)
async def inventory_ip(message: Message, state: FSMContext):
    raw = message.text.strip()
    try:
        ipaddress.ip_address(raw)
    except ValueError:
        await message.answer(
            "Это не похоже на IP-адрес. Введите, например, 10.0.0.5, "
            "или нажмите «Пропустить».",
            reply_markup=skip_keyboard(),
        )
        return
    await state.update_data(inv_ip=raw)
    await _ask_mac(message, state)


@router.callback_query(InventoryStates.waiting_ip, F.data == CB_SKIP)
async def inventory_ip_skip(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await _ask_mac(callback.message, state)


async def _ask_mac(message: Message, state: FSMContext) -> None:
    await state.set_state(InventoryStates.waiting_mac)
    await message.answer(
        "MAC-адрес, если известен (AA:BB:CC:DD:EE:FF):", reply_markup=skip_keyboard()
    )


@router.message(InventoryStates.waiting_mac, F.text)
async def inventory_mac(message: Message, state: FSMContext):
    raw = message.text.strip()
    cleaned = raw.translate(str.maketrans("", "", ":-. ")).upper()
    if len(cleaned) != 12 or any(c not in "0123456789ABCDEF" for c in cleaned):
        await message.answer(
            "MAC должен содержать 12 шестнадцатеричных цифр. Попробуйте ещё раз "
            "или нажмите «Пропустить».",
            reply_markup=skip_keyboard(),
        )
        return
    await state.update_data(inv_mac=raw)
    await _ask_faculty(message, state, message.from_user.id)


@router.callback_query(InventoryStates.waiting_mac, F.data == CB_SKIP)
async def inventory_mac_skip(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await _ask_faculty(callback.message, state, callback.from_user.id)


async def _ask_faculty(message: Message, state: FSMContext, telegram_id: int) -> None:
    await state.set_state(InventoryStates.waiting_faculty)
    ok, faculties = await run_api(message, api_client.get_faculties(telegram_id))
    if not ok:
        return
    await send_picker(
        message, state, "faculty", faculties,
        prompt="Факультет, где стоит устройство:",
        empty_text="Факультетов пока нет — их создаёт администратор в веб-панели.",
    )


@router.callback_query(InventoryStates.waiting_faculty, F.data.startswith("pick:faculty:"))
async def inventory_faculty(callback: CallbackQuery, state: FSMContext):
    faculty_id = int(callback.data.split(":")[2])
    await callback.answer()
    await state.set_state(InventoryStates.waiting_room)

    ok, rooms = await run_api(
        callback.message, api_client.list_rooms(callback.from_user.id, faculty_id)
    )
    if not ok:
        return
    await send_picker(
        callback.message, state, "room", rooms,
        prompt="Кабинет:",
        empty_text="В этом факультете ещё нет кабинетов — сначала добавьте кабинет.",
    )


@router.callback_query(InventoryStates.waiting_room, F.data.startswith("pick:room:"))
async def inventory_room(callback: CallbackQuery, state: FSMContext):
    room_id = int(callback.data.split(":")[2])
    await state.update_data(inv_room_id=room_id)
    await callback.answer()
    await state.set_state(InventoryStates.waiting_employee)

    ok, employees = await run_api(
        callback.message, api_client.list_employees(callback.from_user.id, room_id)
    )
    if not ok:
        return
    shown = await send_picker(
        callback.message, state, "employee", employees,
        prompt="За кем закреплено устройство?",
        empty_text="",
        label_key="full_name",
        extra_rows=[new_employee_row()],
    )
    if not shown:
        # В кабинете ещё нет сотрудников — сразу заводим владельца.
        await callback.message.answer(
            "В этом кабинете пока нет сотрудников — создадим владельца."
        )
        await begin_employee_wizard(callback.message, state, return_to="inventory")


@router.callback_query(InventoryStates.waiting_employee, F.data.startswith("pick:employee:"))
async def inventory_employee(callback: CallbackQuery, state: FSMContext):
    employee_id = int(callback.data.split(":")[2])
    await callback.answer()
    await finalize_inventory(callback.message, state, callback.from_user.id, employee_id)


@router.callback_query(InventoryStates.waiting_employee, F.data == "wiz_new_employee")
async def inventory_new_employee(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await begin_employee_wizard(callback.message, state, return_to="inventory")


# ── Назначение существующего оборудования ────────────────────────────────────

@router.message(F.text == BTN_ASSIGN)
async def start_assign_wizard(message: Message, state: FSMContext):
    if not await ensure_authorized(message):
        return
    await state.clear()
    await state.set_state(AssignStates.waiting_faculty)

    ok, faculties = await run_api(message, api_client.get_faculties(message.from_user.id))
    if not ok:
        return
    await send_picker(
        message, state, "faculty", faculties,
        prompt="Факультет:",
        empty_text="Факультетов пока нет — их создаёт администратор в веб-панели.",
    )


@router.callback_query(AssignStates.waiting_faculty, F.data.startswith("pick:faculty:"))
async def assign_faculty(callback: CallbackQuery, state: FSMContext):
    faculty_id = int(callback.data.split(":")[2])
    await callback.answer()
    await state.set_state(AssignStates.waiting_room)

    ok, rooms = await run_api(
        callback.message, api_client.list_rooms(callback.from_user.id, faculty_id)
    )
    if not ok:
        return
    await send_picker(
        callback.message, state, "room", rooms,
        prompt="Кабинет:",
        empty_text="В этом факультете ещё нет кабинетов.",
    )


@router.callback_query(AssignStates.waiting_room, F.data.startswith("pick:room:"))
async def assign_room(callback: CallbackQuery, state: FSMContext):
    room_id = int(callback.data.split(":")[2])
    await state.update_data(assign_room_id=room_id)
    await callback.answer()
    await state.set_state(AssignStates.waiting_item)

    ok, items = await run_api(
        callback.message, api_client.list_inventory(callback.from_user.id, room_id)
    )
    if not ok:
        return
    labelled = [
        {
            "id": item["id"],
            "name": f"{item['name']} · {DEVICE_LABELS.get(item.get('device_type'), '—')}",
        }
        for item in items
    ]
    await send_picker(
        callback.message, state, "item", labelled,
        prompt="Какое устройство переназначаем?",
        empty_text="В этом кабинете нет зарегистрированного оборудования.",
    )


@router.callback_query(AssignStates.waiting_item, F.data.startswith("pick:item:"))
async def assign_item(callback: CallbackQuery, state: FSMContext):
    await state.update_data(assign_item_id=int(callback.data.split(":")[2]))
    await callback.answer()
    await state.set_state(AssignStates.waiting_employee)

    data = await state.get_data()
    ok, employees = await run_api(
        callback.message,
        api_client.list_employees(callback.from_user.id, data["assign_room_id"]),
    )
    if not ok:
        return
    await send_picker(
        callback.message, state, "employee", employees,
        prompt="Кому назначаем?",
        empty_text="В этом кабинете нет сотрудников.",
        label_key="full_name",
    )


@router.callback_query(AssignStates.waiting_employee, F.data.startswith("pick:employee:"))
async def assign_employee(callback: CallbackQuery, state: FSMContext):
    employee_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    await callback.answer()

    ok, item = await run_api(
        callback.message,
        api_client.assign_inventory(
            callback.from_user.id, data["assign_item_id"], employee_id
        ),
    )
    if not ok:
        return
    await state.clear()
    await callback.message.answer(
        f"✅ «{item['name']}» закреплено за сотрудником (id {employee_id}).",
        reply_markup=admin_menu_keyboard(),
    )
