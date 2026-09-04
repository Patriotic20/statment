import logging
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import api_client
from keyboards.admin_menu import admin_menu_keyboard
from states import WorkerAuthStates

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    # Токен нужен не только для уведомлений, но и для работы со справочниками,
    # а живёт он в памяти процесса — после рестарта бота логин спрашиваем снова.
    if api_client.get_token(telegram_id) is not None:
        await state.clear()
        await message.answer(
            "Siz allaqachon tizimdasiz. Fakultetingiz arizalari haqida xabar "
            "olasiz va ma'lumot qo'sha olasiz.",
            reply_markup=admin_menu_keyboard(),
        )
        return

    await state.set_state(WorkerAuthStates.waiting_username)
    await message.answer(
        "RRTM tizimiga xush kelibsiz!\n"
        "Arizalarni olish uchun tizimga kirishingiz kerak.\n\n"
        "Loginni kiriting:"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=admin_menu_keyboard())


@router.message(WorkerAuthStates.waiting_username)
async def process_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await state.set_state(WorkerAuthStates.waiting_password)
    await message.answer("Parolni kiriting:")


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
            "Login yoki parol noto'g'ri. Qaytadan urinib ko'ring.\n\n"
            "Loginni kiriting:"
        )
        return

    await state.clear()

    # Факультет берём из аккаунта (назначен админом) — не спрашиваем.
    faculty_id = result.get("faculty_id")
    if not faculty_id:
        await message.answer(
            "Tizimga kirdingiz!\n"
            "Sizga hali fakultet biriktirilmagan — administrator biriktirgach, "
            "xabarlar kela boshlaydi.",
            reply_markup=admin_menu_keyboard(),
        )
        return

    faculties = []
    try:
        faculties = await api_client.get_faculties(telegram_id)
    except Exception as exc:
        logger.warning("Не удалось получить список факультетов: %s", exc)
    faculty_name = next(
        (f["name"] for f in faculties if f["id"] == faculty_id), str(faculty_id)
    )
    await message.answer(
        f"Ro'yxatdan o'tdingiz!\n"
        f"Fakultetingiz: {faculty_name}\n"
        f"Shu fakultetning yangi arizalari haqida xabar olasiz.",
        reply_markup=admin_menu_keyboard(),
    )
