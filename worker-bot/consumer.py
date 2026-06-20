import json
import logging
import aio_pika
from aiogram import Bot
from config import settings
from keyboards.issue_actions import issue_actions_keyboard
import api_client

logger = logging.getLogger(__name__)

ISSUE_TYPE_LABELS = {
    "computer": "💻 Компьютер",
    "network": "🌐 Сеть",
    "printer": "🖨 Принтер",
}


async def notify_workers(bot: Bot, issue_id: int):
    faculty_id = await api_client.get_faculty_id_for_issue(issue_id)
    if not faculty_id:
        logger.error(f"Cannot determine faculty for issue {issue_id}, skipping notification")
        return

    worker_ids = await api_client.get_worker_telegram_ids(faculty_id)
    if not worker_ids:
        logger.warning(f"No workers registered for faculty {faculty_id}, notification not sent")
        return

    issue = await api_client.get_issue(issue_id)
    if not issue:
        logger.error(f"Could not fetch issue {issue_id}, skipping notification")
        return

    issue_type = ISSUE_TYPE_LABELS.get(issue["issue_type"], issue["issue_type"])
    created_at = issue.get("created_at", "")
    if created_at:
        # ISO string "2026-06-20T08:52:48+05:00" → "2026-06-20 08:52"
        created_at = created_at.replace("T", " ")[:16]

    text = (
        f"🔔 Новая заявка #{issue_id}\n"
        f"Тип: {issue_type}\n"
        f"Сотрудник: {issue['employee_name']}\n"
        f"ЖШИР: {issue['employee_jshir']}\n"
        f"Кабинет: {issue['room_name']} ({issue['floor']} этаж)\n"
        f"Факультет: {issue['faculty_name']}\n"
        f"Статус: 🆕 Новая"
    )
    if created_at:
        text += f"\nВремя: {created_at}"
    keyboard = issue_actions_keyboard(issue_id)

    for telegram_id in worker_ids:
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup=keyboard,
            )
        except Exception as e:
            logger.error(f"Failed to notify worker {telegram_id}: {e}")

    logger.info(f"Notified {len(worker_ids)} worker(s) about issue {issue_id} (faculty {faculty_id})")


async def start_consumer(bot: Bot):
    logger.info("Connecting to RabbitMQ consumer...")
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue("worker_tasks", durable=True)

        logger.info("Worker bot consumer started, waiting for tasks...")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body)
                        issue_id = data["issue_id"]
                        logger.info(f"Received task for issue_id={issue_id}")
                        await notify_workers(bot, issue_id)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
