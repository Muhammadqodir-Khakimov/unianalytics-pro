"""chat_id -> JWT token saqlash.

Redis URL berilgan bo'lsa — Redis'ga, aks holda in-memory dict'ga saqlanadi.
In-memory rejim faqat dev/test uchun mos (process restart'da yo'qoladi).
"""
from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from ..config import settings


_TOKEN_KEY = "bot:auth:{chat_id}"
_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 kun


class _InMemoryStore:
    """RAM-da saqlovchi fallback (Redis bo'lmaganda)."""

    def __init__(self) -> None:
        self._data: dict[int, dict[str, Any]] = {}

    async def save(self, chat_id: int, payload: dict[str, Any]) -> None:
        self._data[chat_id] = payload

    async def load(self, chat_id: int) -> dict[str, Any] | None:
        return self._data.get(chat_id)

    async def clear(self, chat_id: int) -> None:
        self._data.pop(chat_id, None)

    async def close(self) -> None:
        self._data.clear()


class _RedisStore:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def save(self, chat_id: int, payload: dict[str, Any]) -> None:
        await self._redis.set(
            _TOKEN_KEY.format(chat_id=chat_id),
            json.dumps(payload),
            ex=_TTL_SECONDS,
        )

    async def load(self, chat_id: int) -> dict[str, Any] | None:
        raw = await self._redis.get(_TOKEN_KEY.format(chat_id=chat_id))
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def clear(self, chat_id: int) -> None:
        await self._redis.delete(_TOKEN_KEY.format(chat_id=chat_id))

    async def close(self) -> None:
        await self._redis.aclose()


class AuthStore:
    def __init__(self, redis: Redis | None = None) -> None:
        if redis is not None:
            self._impl: _RedisStore | _InMemoryStore = _RedisStore(redis)
        elif settings.redis_url:
            self._impl = _RedisStore(
                Redis.from_url(settings.redis_url, decode_responses=True)
            )
        else:
            self._impl = _InMemoryStore()

    async def close(self) -> None:
        await self._impl.close()

    async def save(
        self,
        chat_id: int,
        *,
        access_token: str,
        refresh_token: str | None = None,
        user: dict[str, Any] | None = None,
    ) -> None:
        await self._impl.save(chat_id, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user or {},
        })

    async def get(self, chat_id: int) -> dict[str, Any] | None:
        return await self._impl.load(chat_id)

    async def get_token(self, chat_id: int) -> str | None:
        data = await self.get(chat_id)
        return data["access_token"] if data else None

    async def clear(self, chat_id: int) -> None:
        await self._impl.clear(chat_id)


auth_store = AuthStore()
