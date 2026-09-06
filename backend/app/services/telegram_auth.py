"""Проверка подписи Telegram Mini App (initData).

Telegram передаёт в веб-приложение строку initData, подписанную ключом,
производным от токена бота. Проверять её обязательно: страница приложения
открыта всему интернету, и без проверки любой мог бы представиться чужим
telegram_id.

Схема из документации Bot API:
    secret_key = HMAC_SHA256(key="WebAppData", msg=<bot token>)
    hash       = HMAC_SHA256(key=secret_key, msg=<data_check_string>)
где data_check_string — все пары «ключ=значение», кроме hash, отсортированные
по ключу и склеенные через \n.
"""
import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import parse_qsl


class InitDataError(Exception):
    """initData не прошла проверку: подделана, просрочена или повреждена."""


def parse_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86400) -> dict[str, Any]:
    """Проверяет подпись initData и возвращает её разобранные поля.

    Бросает InitDataError, если подпись не совпала или данные слишком старые.
    """
    if not bot_token:
        raise InitDataError("Mini App uchun bot tokeni sozlanmagan")
    if not init_data:
        raise InitDataError("Telegram ma'lumotlari topilmadi")

    try:
        pairs = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError as exc:
        raise InitDataError("Telegram ma'lumotlari buzilgan") from exc

    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InitDataError("Imzo topilmadi")

    data_check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # compare_digest — чтобы время сравнения не зависело от данных.
    if not hmac.compare_digest(expected, received_hash):
        raise InitDataError("Imzo noto'g'ri")

    auth_date = pairs.get("auth_date")
    if auth_date is None or not auth_date.isdigit():
        raise InitDataError("auth_date noto'g'ri")
    if time.time() - int(auth_date) > max_age_seconds:
        raise InitDataError("Sessiya muddati tugadi, ilovani qaytadan oching")

    return pairs


def extract_telegram_id(pairs: dict[str, Any]) -> int:
    """Достаёт telegram_id из проверенных полей initData."""
    raw_user = pairs.get("user")
    if not raw_user:
        raise InitDataError("Foydalanuvchi ma'lumotlari topilmadi")
    try:
        user = json.loads(raw_user)
        return int(user["id"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise InitDataError("Foydalanuvchi ma'lumotlari buzilgan") from exc
