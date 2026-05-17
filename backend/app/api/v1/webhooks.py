"""Webhook konfiguratsiya endpointlari."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_oltp_db
from app.models.oltp.tenant import Webhook

router = APIRouter(prefix="/webhooks", tags=["Webhooks"], dependencies=[Depends(require_admin)])


class WebhookCreate(BaseModel):
    name: str
    url: HttpUrl
    secret: str | None = None
    events: str  # vergul ajratilgan: "grade.created,application.approved" yoki "*"


@router.get("")
def list_webhooks(db: Session = Depends(get_oltp_db)):
    items = db.query(Webhook).order_by(Webhook.created_at.desc()).all()
    return [
        {
            "id": w.id,
            "name": w.name,
            "url": w.url,
            "events": w.events,
            "is_active": w.is_active,
            "failure_count": w.failure_count,
            "last_called_at": w.last_called_at.isoformat() if w.last_called_at else None,
        }
        for w in items
    ]


@router.post("")
def create_webhook(payload: WebhookCreate, db: Session = Depends(get_oltp_db)):
    w = Webhook(
        name=payload.name,
        url=str(payload.url),
        secret=payload.secret,
        events=payload.events,
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return {"id": w.id, "success": True}


@router.put("/{webhook_id}/toggle")
def toggle_webhook(webhook_id: int, is_active: bool, db: Session = Depends(get_oltp_db)):
    w = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not w:
        raise HTTPException(404)
    w.is_active = is_active
    w.failure_count = 0 if is_active else w.failure_count
    db.commit()
    return {"success": True}


@router.delete("/{webhook_id}")
def delete_webhook(webhook_id: int, db: Session = Depends(get_oltp_db)):
    w = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not w:
        raise HTTPException(404)
    db.delete(w)
    db.commit()
    return {"success": True}


@router.post("/{webhook_id}/test")
def test_webhook(webhook_id: int, db: Session = Depends(get_oltp_db)):
    """Webhook ni test qilish — test event yuborish."""
    from app.services.webhook_service import _send_webhook

    w = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not w:
        raise HTTPException(404)
    ok = _send_webhook(w, "test.ping", {"message": "Test webhook from Student OLAP"}, db)
    return {"success": ok}


@router.get("/events/list")
def event_types():
    """Qo'llab-quvvatlanadigan event turlari ro'yxati."""
    return [
        {"code": "*", "description": "Hammasi"},
        {"code": "grade.created", "description": "Yangi baho qo'shildi"},
        {"code": "grade.updated", "description": "Baho o'zgartirildi"},
        {"code": "student.created", "description": "Yangi talaba"},
        {"code": "application.submitted", "description": "Ariza yuborildi"},
        {"code": "application.approved", "description": "Ariza tasdiqlandi"},
        {"code": "application.rejected", "description": "Ariza rad etildi"},
        {"code": "payment.received", "description": "To'lov olindi"},
        {"code": "announcement.created", "description": "E'lon e'lon qilindi"},
        {"code": "thesis.defended", "description": "Bitiruv ishi himoya qilindi"},
    ]
