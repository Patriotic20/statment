import logging
from typing import Any, Optional
import aiohttp
from config import settings

logger = logging.getLogger(__name__)

# JWT воркеров, выданные бэкендом при авторизации: telegram_id → токен.
# Живут в памяти процесса: после рестарта бота воркеру нужно снова /start.
_tokens: dict[int, str] = {}


def set_token(telegram_id: int, token: Optional[str]) -> None:
    if token:
        _tokens[telegram_id] = token


def get_token(telegram_id: int) -> Optional[str]:
    return _tokens.get(telegram_id)


def forget_token(telegram_id: int) -> None:
    _tokens.pop(telegram_id, None)


def _extract_detail(payload: Any, fallback: str) -> str:
    """Достаёт человекочитаемую причину ошибки из ответа FastAPI.

    `detail` — строка для наших HTTPException и список объектов для 422
    от pydantic (например, кривой MAC-адрес).
    """
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list) and detail:
            messages = [
                str(item.get("msg", "")).replace("Value error, ", "")
                for item in detail
                if isinstance(item, dict)
            ]
            joined = "; ".join(m for m in messages if m)
            if joined:
                return joined
    return fallback


class ApiError(Exception):
    """Ошибка запроса к бэкенду с текстом, который можно показать в чате."""

    def __init__(self, message: str, status: int = 0):
        super().__init__(message)
        self.message = message
        self.status = status


async def _request(
    method: str,
    path: str,
    telegram_id: int,
    *,
    json: Any = None,
    params: dict[str, Any] | None = None,
    data: aiohttp.FormData | None = None,
) -> Any:
    """Авторизованный запрос к бэкенду от имени воркера.

    Бросает ApiError с готовым текстом для пользователя.
    """
    token = get_token(telegram_id)
    if not token:
        raise ApiError("Сессия не найдена. Отправьте /start и авторизуйтесь заново.", 401)

    url = f"{settings.api_base_url}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method, url, headers=headers, json=json, params=params, data=data
        ) as response:
            if response.status == 204:
                return None
            try:
                payload = await response.json()
            except Exception:
                payload = None

            if response.status == 401:
                forget_token(telegram_id)
                raise ApiError(
                    "Сессия истекла. Отправьте /start и авторизуйтесь заново.", 401
                )
            if response.status >= 400:
                message = _extract_detail(payload, f"Ошибка сервера (HTTP {response.status})")
                logger.warning("%s %s → HTTP %s: %s", method, path, response.status, message)
                raise ApiError(message, response.status)
            return payload


# ── Заявки (используются consumer'ом и обработчиками кнопок) ──────────────────

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


# ── Авторизация воркера ──────────────────────────────────────────────────────

async def worker_auth(telegram_id: int, username: str, password: str) -> dict[str, Any] | None:
    """Авторизует воркера. Возвращает JSON ответа (ok, user_id, faculty_id,
    access_token) при успехе или None при неверных учётных данных.
    Токен сохраняется, чтобы бот мог работать со справочниками."""
    url = f"{settings.api_base_url}/telegram/worker/auth"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            "telegram_id": telegram_id,
            "username": username,
            "password": password,
        }) as response:
            if response.status == 200:
                data = await response.json()
                set_token(telegram_id, data.get("access_token"))
                return data
            logger.warning(f"Worker auth failed for {username}: HTTP {response.status}")
            return None


async def check_worker(telegram_id: int) -> bool:
    url = f"{settings.api_base_url}/telegram/workers/{telegram_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.status == 200


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


# ── Справочники (требуют токена воркера) ─────────────────────────────────────

async def get_faculties(telegram_id: int) -> list[dict[str, Any]]:
    return await _request("GET", "/faculties/", telegram_id)


async def list_rooms(telegram_id: int, faculty_id: int) -> list[dict[str, Any]]:
    return await _request(
        "GET", "/rooms/", telegram_id, params={"faculty_id": faculty_id, "limit": 100}
    )


async def create_room(
    telegram_id: int, name: str, floor: int, faculty_id: int
) -> dict[str, Any]:
    return await _request(
        "POST", "/rooms/", telegram_id,
        json={"name": name, "floor": floor, "faculty_id": faculty_id},
    )


async def list_employees(telegram_id: int, room_id: int) -> list[dict[str, Any]]:
    return await _request(
        "GET", "/employees/", telegram_id, params={"room_id": room_id, "limit": 100}
    )


async def find_employee_by_jshir(telegram_id: int, jshir: str) -> dict[str, Any] | None:
    found = await _request("GET", "/employees/", telegram_id, params={"jshir": jshir})
    return found[0] if found else None


async def create_employee(
    telegram_id: int, jshir: str, full_name: str, room_id: int
) -> dict[str, Any]:
    return await _request(
        "POST", "/employees/", telegram_id,
        json={"jshir": jshir, "full_name": full_name, "room_id": room_id},
    )


async def list_inventory(telegram_id: int, room_id: int) -> list[dict[str, Any]]:
    return await _request(
        "GET", "/inventory/", telegram_id, params={"room_id": room_id, "limit": 100}
    )


async def create_inventory(telegram_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return await _request("POST", "/inventory/", telegram_id, json=payload)


async def assign_inventory(
    telegram_id: int, inventory_id: int, employee_id: int
) -> dict[str, Any]:
    return await _request(
        "PATCH", f"/inventory/{inventory_id}", telegram_id,
        json={"employee_id": employee_id},
    )


async def upload_inventory_photo(
    telegram_id: int, inventory_id: int, content: bytes, filename: str, content_type: str
) -> dict[str, Any]:
    form = aiohttp.FormData()
    form.add_field("file", content, filename=filename, content_type=content_type)
    return await _request(
        "POST", f"/inventory/{inventory_id}/photo", telegram_id, data=form
    )
