# Пакет для HTTP запросов к вашему основному Backend API
import aiohttp
from config import settings


async def get_client(telegram_id: int) -> dict | None:
    """Возвращает привязанного клиента или None, если связь не найдена (404)."""
    url = f"{settings.api_base_url}/telegram/clients/{telegram_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return None


async def link_client(
    telegram_id: int,
    jshir: str,
    username: str | None,
    first_name: str | None,
) -> tuple[bool, str]:
    """Привязывает Telegram-аккаунт к сотруднику по ЖШИР.

    Возвращает (успех, сообщение об ошибке).
    """
    url = f"{settings.api_base_url}/telegram/link"
    payload = {
        "telegram_id": telegram_id,
        "jshir": jshir,
        "username": username,
        "first_name": first_name,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                return True, ""
            try:
                data = await resp.json()
                detail = data.get("detail", "Не удалось привязать ЖШИР")
                if isinstance(detail, list):
                    detail = "Неверный формат ЖШИР"
            except Exception:
                detail = "Не удалось привязать ЖШИР"
            return False, detail


async def create_issue(telegram_id: int, issue_type: str) -> tuple[bool, str]:
    """Создаёт заявку в backend.

    Возвращает (успех, сообщение об ошибке). При ошибке достаёт текст из
    поля ``detail`` ответа, чтобы показать сотруднику конкретную причину.
    """
    url = f"{settings.api_base_url}/issues/"
    payload = {"telegram_id": telegram_id, "issue_type": issue_type}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                return True, ""
            try:
                data = await resp.json()
                detail = data.get("detail", "")
                if isinstance(detail, list):
                    detail = ""
            except Exception:
                detail = ""
            return False, detail
