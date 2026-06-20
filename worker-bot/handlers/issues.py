import logging
from aiogram import Router
from aiogram.types import CallbackQuery

import api_client
from keyboards.issue_actions import issue_actions_keyboard

logger = logging.getLogger(__name__)

router = Router()

ISSUE_TYPE_LABELS = {
    "computer": "💻 Компьютер",
    "network": "🌐 Сеть",
    "printer": "🖨 Принтер",
}

STATUS_LABELS = {
    "new": "🆕 Новая",
    "in_progress": "🔧 В работе",
    "resolved": "✅ Решена",
}


@router.callback_query(lambda c: c.data and c.data.startswith("accept:"))
async def accept_issue(callback: CallbackQuery):
    issue_id = int(callback.data.split(":")[1])
    issue = await api_client.update_issue_status(issue_id, "in_progress")
    if issue:
        issue_type = ISSUE_TYPE_LABELS.get(issue["issue_type"], issue["issue_type"])
        await callback.message.edit_text(
            f"Заявка #{issue_id} — {issue_type}\n"
            f"Статус: {STATUS_LABELS['in_progress']}\n"
            f"Исполнитель: {callback.from_user.full_name}",
            reply_markup=issue_actions_keyboard(issue_id),
        )
    await callback.answer("Принято в работу!")


@router.callback_query(lambda c: c.data and c.data.startswith("resolve:"))
async def resolve_issue(callback: CallbackQuery):
    issue_id = int(callback.data.split(":")[1])
    issue = await api_client.update_issue_status(issue_id, "resolved")
    if issue:
        issue_type = ISSUE_TYPE_LABELS.get(issue["issue_type"], issue["issue_type"])
        await callback.message.edit_text(
            f"Заявка #{issue_id} — {issue_type}\n"
            f"Статус: {STATUS_LABELS['resolved']}\n"
            f"Закрыл: {callback.from_user.full_name}",
        )
    await callback.answer("Заявка закрыта!")
