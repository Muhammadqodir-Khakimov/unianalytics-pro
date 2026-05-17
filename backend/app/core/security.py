"""JWT tokenlar va parol hashlash."""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app.core.exceptions import CredentialsException

BCRYPT_MAX_BYTES = 72


def _to_bytes(password: str) -> bytes:
    """Bcrypt 72 byte limitiga moslash."""
    raw = password.encode("utf-8")
    return raw[:BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    """Parolni bcrypt orqali hashlash."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_to_bytes(password), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Parolni tekshirish."""
    try:
        return bcrypt.checkpw(_to_bytes(plain_password), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    """Access JWT token yaratish."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> str:
    """Refresh JWT token yaratish."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Tokenni decode qilish, yaroqsiz bo'lsa CredentialsException."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        raise CredentialsException(f"Token yaroqsiz: {e}") from e
