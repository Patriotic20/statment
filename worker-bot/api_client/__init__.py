import logging
from typing import Any
import aiohttp
from config import settings

logger = logging.getLogger(__name__)


async def get_issue(issue_id: int) -> dict[str, Any] | None:
    url = f"{settings.api_base_url}/telegram/issues/{issue_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            logger.error(f"Failed to fetch issue {issue_id}: HTTP {response.status}")
            return None


async def update_issue_status(issue_id: int, status: str) -> dict[str, Any] | None:
    url = f"{settings.api_base_url}/telegram/issues/{issue_id}"
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, json={"status": status}) as response:
            if response.status == 200:
                return await response.json()
            logger.error(f"Failed to update issue {issue_id} status: HTTP {response.status}")
            return None


async def worker_auth(telegram_id: int, username: str, password: str) -> dict[str, Any] | None:
    """Авторизует воркера. Возвращает JSON ответа (ok, user_id, faculty_id)
    при успехе или None при неверных учётных данных."""
    url = f"{settings.api_base_url}/telegram/worker/auth"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            "telegram_id": telegram_id,
            "username": username,
            "password": password,
        }) as response:
            if response.status == 200:
                return await response.json()
            logger.warning(f"Worker auth failed for {username}: HTTP {response.status}")
            return None


async def check_worker(telegram_id: int) -> bool:
    url = f"{settings.api_base_url}/telegram/workers/{telegram_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.status == 200


async def get_faculties() -> list[dict[str, Any]]:
    url = f"{settings.api_base_url}/faculties/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            logger.error(f"Failed to fetch faculties: HTTP {response.status}")
            return []


async def set_worker_faculty(telegram_id: int, faculty_id: int) -> bool:
    url = f"{settings.api_base_url}/telegram/worker/faculty"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            "telegram_id": telegram_id,
            "faculty_id": faculty_id,
        }) as response:
            if response.status == 200:
                return True
            logger.error(f"Failed to set faculty for worker {telegram_id}: HTTP {response.status}")
            return False


async def get_faculty_id_for_issue(issue_id: int) -> int | None:
    url = f"{settings.api_base_url}/telegram/issue-faculty/{issue_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["faculty_id"]
            logger.error(f"Failed to get faculty for issue {issue_id}: HTTP {response.status}")
            return None


async def get_worker_telegram_ids(faculty_id: int) -> list[int]:
    url = f"{settings.api_base_url}/telegram/workers"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"faculty_id": faculty_id}) as response:
            if response.status == 200:
                data = await response.json()
                return [item["telegram_id"] for item in data]
            logger.error(f"Failed to fetch workers for faculty {faculty_id}: HTTP {response.status}")
            return []
