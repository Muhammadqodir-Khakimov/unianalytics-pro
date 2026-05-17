"""Oddiy in-memory cache (Redis o'rniga LRU + TTL).

Production da Redis bilan almashtirish kerak — interface bir xil saqlanadi.
"""
import time
from functools import wraps
from typing import Any, Callable
from collections import OrderedDict


class TTLCache:
    """LRU + TTL cache."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Any:
        if key not in self._store:
            return None
        expires_at, value = self._store[key]
        if time.time() > expires_at:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires_at = time.time() + (ttl or self.default_ttl)
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (expires_at, value)
        while len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def invalidate(self, prefix: str = "") -> int:
        """Prefiks bilan boshlanadigan barcha keylarni o'chirish."""
        keys = [k for k in self._store if k.startswith(prefix)]
        for k in keys:
            del self._store[k]
        return len(keys)

    def stats(self) -> dict:
        return {"size": len(self._store), "max_size": self.max_size}


cache = TTLCache(max_size=2000, default_ttl=300)


def cached(prefix: str, ttl: int = 300):
    """Funksiya natijasini cache lash decorator."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key_parts = [prefix, fn.__name__]
            key_parts.extend(str(a) for a in args[1:])  # session ni o'tkazib yubor
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = ":".join(key_parts)

            hit = cache.get(key)
            if hit is not None:
                return hit
            result = fn(*args, **kwargs)
            cache.set(key, result, ttl)
            return result

        return wrapper

    return decorator
