"""Auth middleware — har bir update uchun Redis dan token oladi va `data`
ga qo'shadi. Handler'lar `token: str | None` ni parametr sifatida qabul
qilishi mumkin.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser

from ..services.auth_store import auth_store


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        if tg_user is not None:
            stored = await auth_store.get(tg_user.id)
            data["token"] = stored.get("access_token") if stored else None
            data["user"] = stored.get("user") if stored else None
        else:
            data["token"] = None
            data["user"] = None
        return await handler(event, data)
