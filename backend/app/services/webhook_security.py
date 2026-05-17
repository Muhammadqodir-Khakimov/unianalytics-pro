"""Webhook signature verification va idempotency.

Production'da har bir to'lov webhook'iga:
1. Signature/HMAC verify qilinishi kerak (replay attack himoyasi)
2. Idempotency key tekshirilishi kerak (duplicate POST himoyasi)

Stripe: `Stripe-Signature` header HMAC-SHA256 with webhook secret
Click: `sign_string` MD5(secret + click_trans_id + ...)
Payme: HTTP Basic auth (Authorization: Basic ...)
"""
import base64
import hashlib
import hmac
import os
import time
from typing import Any

from loguru import logger


# In-memory idempotency store; production'da Redis ishlatish kerak.
# {key: timestamp} — eski yozuvlar avtomatik tozalanadi
_idempotency_seen: dict[str, float] = {}
_IDEMPOTENCY_TTL_SEC = 24 * 3600  # 24 soat


def _gc_idempotency() -> None:
    """Eski idempotency kalitlarini tozalash."""
    now = time.time()
    expired = [k for k, ts in _idempotency_seen.items() if now - ts > _IDEMPOTENCY_TTL_SEC]
    for k in expired:
        _idempotency_seen.pop(k, None)


def is_duplicate(idempotency_key: str) -> bool:
    """True qaytarsa — bu webhook avval qayta ishlangan, takror ishlatmang."""
    if not idempotency_key:
        return False
    _gc_idempotency()
    if idempotency_key in _idempotency_seen:
        logger.warning("Duplicate webhook idempotency key: {}", idempotency_key)
        return True
    _idempotency_seen[idempotency_key] = time.time()
    return False


# ============================================================
# Stripe
# ============================================================

def verify_stripe_signature(payload: bytes, sig_header: str, secret: str | None = None, tolerance: int = 300) -> bool:
    """Stripe webhook signature verification.

    Format: `t=<timestamp>,v1=<sig>,v0=<sig>` (sig = HMAC-SHA256(secret, t.body))
    """
    secret = secret or os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    if not secret or not sig_header:
        return False

    parts = {}
    for kv in sig_header.split(","):
        if "=" in kv:
            k, v = kv.split("=", 1)
            parts.setdefault(k, []).append(v)

    try:
        ts = int(parts.get("t", [""])[0])
    except (ValueError, IndexError):
        return False

    # Replay protection: too old
    if abs(time.time() - ts) > tolerance:
        logger.warning("Stripe webhook outside tolerance: ts={}", ts)
        return False

    signed_payload = f"{ts}.".encode() + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()

    for v1 in parts.get("v1", []):
        if hmac.compare_digest(expected, v1):
            return True
    return False


# ============================================================
# Click
# ============================================================

def verify_click_signature(payload: dict[str, Any], received_sign: str, secret: str | None = None) -> bool:
    """Click signature: MD5(click_trans_id + service_id + secret + merchant_trans_id + amount + action + sign_time)."""
    secret = secret or os.environ.get("CLICK_SECRET_KEY", "")
    if not secret:
        return False
    raw = (
        f"{payload.get('click_trans_id', '')}"
        f"{payload.get('service_id', '')}"
        f"{secret}"
        f"{payload.get('merchant_trans_id', '')}"
        f"{payload.get('amount', '')}"
        f"{payload.get('action', '')}"
        f"{payload.get('sign_time', '')}"
    )
    expected = hashlib.md5(raw.encode()).hexdigest()
    return hmac.compare_digest(expected, received_sign or "")


# ============================================================
# Payme (HTTP Basic auth)
# ============================================================

def verify_payme_auth(authorization_header: str, login: str | None = None, password: str | None = None) -> bool:
    """Payme Authorization: Basic base64(login:password)."""
    login = login or os.environ.get("PAYME_MERCHANT_LOGIN", "Paycom")
    password = password or os.environ.get("PAYME_MERCHANT_KEY", "")
    if not password or not authorization_header:
        return False
    if not authorization_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(authorization_header[6:]).decode()
        u, p = decoded.split(":", 1)
        return hmac.compare_digest(u, login) and hmac.compare_digest(p, password)
    except Exception:
        return False


# ============================================================
# Generic HMAC (for custom webhook providers)
# ============================================================

def verify_hmac_sha256(payload: bytes, signature: str, secret: str) -> bool:
    """Generic HMAC-SHA256 verification."""
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
