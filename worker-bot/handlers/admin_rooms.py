"""Мастер добавления кабинета: название → этаж → факультет."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import api_client
from handlers.admin_common import ensure_authorized, run_api, send_picker
from keyboards.admin_menu import BTN_ROOM, admin_menu_keyboard
from keyboards.pickers import cancel_keyboard, floor_keyboard
from states import RoomStates

router = Router()


@router.message(F.text == BTN_ROOM)
async def start_room_wizard(message: Message, state: FSMContext):
    if not await ensure_authorized(message):
        return
    await state.clear()
    await state.set_state(RoomStates.waiting_name)
    await message.answer(
        "Название кабинета (например, «Кабинет 305»):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RoomStates.waiting_name, F.text)
async def room_name(message: Message, state: FSMContext):
    await state.update_data(room_name=message.text.strip())
    await state.set_state(RoomStates.waiting_floor)
    await message.answer("Этаж:", reply_markup=floor_keyboard())


@router.callback_query(RoomStates.waiting_floor, F.data.startswith("pick:floor:"))
async def room_floor(callback: CallbackQuery, state: FSMContext):
    await state.update_data(room_floor=int(callback.data.split(":")[2]))
    await callback.answer()
    await state.set_state(RoomStates.waiting_faculty)

    ok, faculties = await run_api(
        callback.message, api_client.get_faculties(callback.from_user.id)
    )
    if not ok:
        return
    await send_picker(
        callback.message, state, "faculty", faculties,
        prompt="Выберите факультет:",
        empty_text="Факультетов пока нет — их создаёт администратор в веб-панели.",
    )


@router.callback_query(RoomStates.waiting_faculty, F.data.startswith("pick:faculty:"))
async def room_faculty(callback: CallbackQuery, state: FSMContext):
    faculty_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    await callback.answer()

    ok, room = await run_api(
        callback.message,
        api_client.create_room(
            callback.from_user.id, data["room_name"], data["room_floor"], faculty_id
        ),
    )
    if not ok:
        return
    await state.clear()
    await callback.message.answer(
        f"✅ Кабинет «{room['name']}» создан (этаж {data['room_floor']}, id {room['id']}).",
        reply_markup=admin_menu_keyboard(),
    )
