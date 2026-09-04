"""Мастер добавления сотрудника: ЖШИР → ФИО → факультет → кабинет.

Мастер оборудования переиспользует его, когда владельца нужно завести на месте:
в этом случае кабинет уже выбран, и после создания управление возвращается
к финализации оборудования.
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import api_client
from handlers.admin_common import ensure_authorized, run_api, send_picker
from handlers.inventory_finalize import finalize_inventory
from keyboards.admin_menu import BTN_EMPLOYEE, admin_menu_keyboard
from keyboards.pickers import cancel_keyboard
from states import EmployeeStates

router = Router()


def _clean_jshir(raw: str) -> str | None:
    """ЖШИР — ровно 14 цифр. Проверяем в боте, чтобы не гонять заведомо
    неверное значение на сервер."""
    cleaned = "".join(raw.split())
    return cleaned if cleaned.isdigit() and len(cleaned) == 14 else None


async def begin_employee_wizard(
    message: Message, state: FSMContext, return_to: str | None = None
) -> None:
    """Запускает мастер. `return_to='inventory'` — вернуться в мастер оборудования."""
    await state.update_data(emp_return_to=return_to)
    await state.set_state(EmployeeStates.waiting_jshir)
    await message.answer("ЖШИР сотрудника (14 цифр):", reply_markup=cancel_keyboard())


@router.message(F.text == BTN_EMPLOYEE)
async def start_employee_wizard(message: Message, state: FSMContext):
    if not await ensure_authorized(message):
        return
    await state.clear()
    await begin_employee_wizard(message, state)


@router.message(EmployeeStates.waiting_jshir, F.text)
async def employee_jshir(message: Message, state: FSMContext):
    jshir = _clean_jshir(message.text)
    if jshir is None:
        await message.answer("ЖШИР должен состоять ровно из 14 цифр. Попробуйте ещё раз:")
        return

    ok, existing = await run_api(
        message, api_client.find_employee_by_jshir(message.from_user.id, jshir)
    )
    if not ok:
        return
    if existing is not None:
        await state.clear()
        await message.answer(
            f"Такой сотрудник уже есть: {existing['full_name']} (id {existing['id']}).",
            reply_markup=admin_menu_keyboard(),
        )
        return

    await state.update_data(emp_jshir=jshir)
    await state.set_state(EmployeeStates.waiting_full_name)
    await message.answer("ФИО сотрудника:", reply_markup=cancel_keyboard())


@router.message(EmployeeStates.waiting_full_name, F.text)
async def employee_full_name(message: Message, state: FSMContext):
    await state.update_data(emp_full_name=message.text.strip())
    data = await state.get_data()

    # Пришли из мастера оборудования — кабинет там уже выбран, не спрашиваем.
    if data.get("emp_return_to") == "inventory" and data.get("inv_room_id"):
        await _create_and_continue(message, state, data["inv_room_id"])
        return

    await state.set_state(EmployeeStates.waiting_faculty)
    ok, faculties = await run_api(message, api_client.get_faculties(message.from_user.id))
    if not ok:
        return
    await send_picker(
        message, state, "faculty", faculties,
        prompt="Выберите факультет:",
        empty_text="Факультетов пока нет — их создаёт администратор в веб-панели.",
    )


@router.callback_query(EmployeeStates.waiting_faculty, F.data.startswith("pick:faculty:"))
async def employee_faculty(callback: CallbackQuery, state: FSMContext):
    faculty_id = int(callback.data.split(":")[2])
    await callback.answer()
    await state.set_state(EmployeeStates.waiting_room)

    ok, rooms = await run_api(
        callback.message, api_client.list_rooms(callback.from_user.id, faculty_id)
    )
    if not ok:
        return
    await send_picker(
        callback.message, state, "room", rooms,
        prompt="Выберите кабинет:",
        empty_text="В этом факультете ещё нет кабинетов — сначала добавьте кабинет.",
    )


@router.callback_query(EmployeeStates.waiting_room, F.data.startswith("pick:room:"))
async def employee_room(callback: CallbackQuery, state: FSMContext):
    room_id = int(callback.data.split(":")[2])
    await callback.answer()
    await _create_and_continue(callback.message, state, room_id, callback.from_user.id)


async def _create_and_continue(
    message: Message, state: FSMContext, room_id: int, telegram_id: int | None = None
) -> None:
    telegram_id = telegram_id or message.from_user.id
    data = await state.get_data()

    ok, employee = await run_api(
        message,
        api_client.create_employee(
            telegram_id, data["emp_jshir"], data["emp_full_name"], room_id
        ),
    )
    if not ok:
        return

    if data.get("emp_return_to") == "inventory":
        await message.answer(f"✅ Сотрудник {employee['full_name']} создан. Завершаю оборудование…")
        await finalize_inventory(message, state, telegram_id, employee["id"])
        return

    await state.clear()
    await message.answer(
        f"✅ Сотрудник {employee['full_name']} добавлен (ЖШИР {employee['jshir']}, id {employee['id']}).",
        reply_markup=admin_menu_keyboard(),
    )
