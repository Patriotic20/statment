import logging
from aiogram import Router
from aiogram.types import CallbackQuery

import api_client
from keyboards.issue_actions import issue_actions_keyboard

logger = logging.getLogger(__name__)

router = Router()

ISSUE_TYPE_LABELS = {
    "computer": "💻 Kompyuter",
    "network": "🌐 Tarmoq",
    "printer": "🖨 Printer",
}

STATUS_LABELS = {
    "new": "🆕 Yangi",
    "in_progress": "🔧 Jarayonda",
    "resolved": "✅ Hal qilindi",
}


@router.callback_query(lambda c: c.data and c.data.startswith("accept:"))
async def accept_issue(callback: CallbackQuery):
    issue_id = int(callback.data.split(":")[1])
    issue = await api_client.update_issue_status(issue_id, "in_progress")
    if issue:
        issue_type = ISSUE_TYPE_LABELS.get(issue["issue_type"], issue["issue_type"])
        await callback.message.edit_text(
            f"Ariza #{issue_id} — {issue_type}\n"
            f"Holati: {STATUS_LABELS['in_progress']}\n"
            f"Mas'ul: {callback.from_user.full_name}",
            reply_markup=issue_actions_keyboard(issue_id),
        )
    await callback.answer("Ishga olindi!")


@router.callback_query(lambda c: c.data and c.data.startswith("resolve:"))
async def resolve_issue(callback: CallbackQuery):
    issue_id = int(callback.data.split(":")[1])
    issue = await api_client.update_issue_status(issue_id, "resolved")
    if issue:
        issue_type = ISSUE_TYPE_LABELS.get(issue["issue_type"], issue["issue_type"])
        await callback.message.edit_text(
            f"Ariza #{issue_id} — {issue_type}\n"
            f"Holati: {STATUS_LABELS['resolved']}\n"
            f"Yakunladi: {callback.from_user.full_name}",
        )
    await callback.answer("Ariza yakunlandi!")
