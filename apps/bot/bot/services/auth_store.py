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
_TOKEN_KEY_PREFIX = "bot:auth:"
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

    async def find_by_token(self, access_token: str) -> int | None:
        for cid, payload in self._data.items():
            if payload.get("access_token") == access_token:
                return cid
        return None


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

    async def find_by_token(self, access_token: str) -> int | None:
        """Reverse-lookup: berilgan access_tokenga ega chat_idni topish.

        Redis'da `bot:auth:*` kalitlarini scan qilamiz. Kichik miqyosli bot
        uchun yetarli (yuzlab foydalanuvchilar).
        """
        cursor = 0
        while True:
            cursor, keys = await self._redis.scan(
                cursor=cursor, match=f"{_TOKEN_KEY_PREFIX}*", count=100
            )
            for k in keys:
                raw = await self._redis.get(k)
                if not raw:
                    continue
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if data.get("access_token") == access_token:
                    suffix = k.split(":", 2)[-1] if isinstance(k, str) else k.decode().split(":", 2)[-1]
                    try:
                        return int(suffix)
                    except ValueError:
                        return None
            if cursor == 0:
                break
        return None


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

    async def find_chat_by_token(self, access_token: str) -> int | None:
        return await self._impl.find_by_token(access_token)


auth_store = AuthStore()
