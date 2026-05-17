"""Audit log servisi."""
import json
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.oltp.audit import AuditLog
from app.models.oltp.user import User


def log_action(
    db: Session,
    user: User | None,
    action: str,
    resource_type: str,
    resource_id: str | int | None = None,
    description: str | None = None,
    changes: dict[str, Any] | None = None,
    request: Request | None = None,
) -> None:
    """Audit log yozuvi yaratish.

    Bu funksiya tranzaktsiyani commit qilmaydi — chaqiruvchi commit qiladi.
    """
    entry = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else None,
        user_role=user.role.value if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        description=description,
        changes_json=json.dumps(changes, default=str, ensure_ascii=False) if changes else None,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    db.add(entry)


def list_logs(
    db: Session,
    user_id: int | None = None,
    resource_type: str | None = None,
    action: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    if action:
        q = q.filter(AuditLog.action == action)
    total = q.count()
    items = q.offset(offset).limit(limit).all()
    return {"total": total, "items": items}
