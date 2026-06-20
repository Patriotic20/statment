import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import api_client
from states import WorkerAuthStates

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    already_registered = await api_client.check_worker(telegram_id)
    if already_registered:
        await message.answer("Вы уже авторизованы. Вы получаете уведомления о заявках вашего факультета.")
        return

    await state.set_state(WorkerAuthStates.waiting_username)
    await message.answer(
        "Добро пожаловать в систему RRTM!\n"
        "Для получения заявок необходимо авторизоваться.\n\n"
        "Введите ваш логин:"
    )


@router.message(WorkerAuthStates.waiting_username)
async def process_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await state.set_state(WorkerAuthStates.waiting_password)
    await message.answer("Введите пароль:")


@router.message(WorkerAuthStates.waiting_password)
async def process_password(message: Message, state: FSMContext):
    data = await state.get_data()
    username = data["username"]
    password = message.text.strip()
    telegram_id = message.from_user.id

    result = await api_client.worker_auth(telegram_id, username, password)
    if result is None:
        await state.set_state(WorkerAuthStates.waiting_username)
        await message.answer(
            "Неверный логин или пароль. Попробуйте снова.\n\n"
            "Введите ваш логин:"
        )
        return

    await state.clear()

    # Факультет берём из аккаунта (назначен админом) — не спрашиваем.
    faculty_id = result.get("faculty_id")
    if not faculty_id:
        await message.answer(
            "Авторизация успешна!\n"
            "Факультет вам пока не назначен администратором — "
            "уведомления начнут приходить после назначения."
        )
        return

    faculties = await api_client.get_faculties()
    faculty_name = next((f["name"] for f in faculties if f["id"] == faculty_id), str(faculty_id))
    await message.answer(
        f"Регистрация завершена!\n"
        f"Ваш факультет: {faculty_name}\n"
        f"Вы будете получать уведомления о новых заявках этого факультета."
    )
