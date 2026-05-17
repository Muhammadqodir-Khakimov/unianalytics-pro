"""Webhook tizimi — tashqi tizimlarga event yuborish.

Event turlari:
- grade.created
- grade.updated
- application.submitted
- application.approved
- application.rejected
- student.created
- payment.received
- announcement.created
- thesis.defended
"""
import hashlib
import hmac
import json
from datetime import datetime
from typing import Any

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from app.database import oltp_session
from app.models.oltp.tenant import Webhook


def trigger_event(event_type: str, payload: dict[str, Any]) -> None:
    """Event qaytarish — barcha mos webhook larga yuborish.

    Bu funksiya sinxron, tezda qaytadi. Real production da Celery task ichida bo'lishi kerak.
    """
    with oltp_session() as db:
        webhooks = (
            db.query(Webhook)
            .filter(Webhook.is_active == True)  # noqa: E712
            .all()
        )
        for hook in webhooks:
            events = [e.strip() for e in hook.events.split(",")]
            if event_type in events or "*" in events:
                _send_webhook(hook, event_type, payload, db)


def _send_webhook(hook: Webhook, event_type: str, payload: dict, db: Session) -> bool:
    """Bitta webhook ga POST yuborish."""
    body = {
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
    }
    body_json = json.dumps(body, default=str)

    headers = {"Content-Type": "application/json", "X-Webhook-Event": event_type}

    # HMAC signature
    if hook.secret:
        sig = hmac.new(hook.secret.encode(), body_json.encode(), hashlib.sha256).hexdigest()
        headers["X-Webhook-Signature"] = f"sha256={sig}"

    try:
        with httpx.Client(timeout=10) as client:
            r = client.post(hook.url, content=body_json, headers=headers)
            success = 200 <= r.status_code < 300

        hook.last_called_at = datetime.utcnow()
        if success:
            hook.failure_count = 0
            logger.info("Webhook {} -> {} : OK ({})", event_type, hook.url, r.status_code)
        else:
            hook.failure_count += 1
            logger.warning("Webhook {} -> {} : FAIL ({})", event_type, hook.url, r.status_code)
            # 10 marotaba xato bo'lsa o'chirish
            if hook.failure_count >= 10:
                hook.is_active = False
                logger.error("Webhook {} disabled — juda ko'p xatolar", hook.url)
        db.commit()
        return success
    except Exception as e:
        hook.failure_count += 1
        if hook.failure_count >= 10:
            hook.is_active = False
        db.commit()
        logger.error("Webhook error {}: {}", hook.url, e)
        return False
