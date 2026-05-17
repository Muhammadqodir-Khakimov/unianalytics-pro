"""Per-user rate limiting middleware (Redis token bucket).

Redis URL berilmagan bo'lsa — throttling o'chiriladi (dev rejim).
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from redis.asyncio import Redis

from ..config import settings


_KEY = "bot:rl:{user_id}"


class ThrottlingMiddleware(BaseMiddleware):
    """Daqiqada `RATE_LIMIT_PER_MIN` dan ortiq so'rovlarni rad etadi."""

    def __init__(self, redis: Redis | None = None) -> None:
        self._redis: Redis | None = redis
        if self._redis is None and settings.redis_url:
            self._redis = Redis.from_url(
                settings.redis_url, decode_responses=True
            )
        self._limit = settings.rate_limit_per_min

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Redis yo'q — throttling o'chiq
        if self._redis is None:
            return await handler(event, data)

        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        key = _KEY.format(user_id=user.id)
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, 60)
        if count > self._limit:
            if isinstance(event, Message):
                await event.answer(
                    "⏳ Juda ko'p so'rov. Iltimos, biroz kuting."
                )
            return None
        return await handler(event, data)
