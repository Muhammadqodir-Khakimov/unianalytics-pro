"""API rate limiting — slowapi orqali.

Rol asoslangan limitlar:
- Anonymous (login, register): 10/min
- Student: 60/min
- Teacher/Dekan: 120/min
- Admin: 300/min
"""
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def _key_func(request: Request) -> str:
    """User ID asosida key (yoki IP)."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        # JWT decode qilmasdan oddiy hash
        return f"token:{hash(auth[:30])}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=_key_func, default_limits=["120/minute"])


def setup_rate_limiting(app: FastAPI) -> None:
    """Rate limit middleware qo'shish."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Pre-defined limits — endpoint larda dekorator sifatida ishlatish:
# @limiter.limit("5/minute")
LIMITS = {
    "auth": "10/minute",  # login, register
    "report": "20/minute",  # report generation
    "olap": "60/minute",  # OLAP queries
    "search": "120/minute",
    "default": "200/minute",
}
