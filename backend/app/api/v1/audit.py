"""Audit log endpointlari."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_oltp_db
from app.services import audit_service

router = APIRouter(prefix="/audit", tags=["Audit"], dependencies=[Depends(require_admin)])


@router.get("/logs")
def list_audit_logs(
    user_id: int | None = None,
    resource_type: str | None = None,
    action: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_oltp_db),
):
    """Audit log lar (faqat admin uchun)."""
    result = audit_service.list_logs(
        db,
        user_id=user_id,
        resource_type=resource_type,
        action=action,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    return {
        "total": result["total"],
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": x.id,
                "username": x.username,
                "user_role": x.user_role,
                "action": x.action,
                "resource_type": x.resource_type,
                "resource_id": x.resource_id,
                "description": x.description,
                "ip_address": x.ip_address,
                "created_at": x.created_at.isoformat(),
            }
            for x in result["items"]
        ],
    }


@router.get("/stats")
def audit_stats(db: Session = Depends(get_oltp_db)):
    """Audit statistika — actions, kim ko'p ishlatadi, etc."""
    from collections import Counter
    from app.models.oltp.audit import AuditLog

    logs = db.query(AuditLog).limit(10000).all()
    by_action: Counter = Counter(l.action for l in logs)
    by_user: Counter = Counter(l.username for l in logs if l.username)
    by_resource: Counter = Counter(l.resource_type for l in logs)
    return {
        "total": len(logs),
        "by_action": dict(by_action.most_common(10)),
        "by_user": dict(by_user.most_common(10)),
        "by_resource": dict(by_resource.most_common(10)),
    }
