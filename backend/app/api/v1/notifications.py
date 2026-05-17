"""Notification endpointlari."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_oltp_db
from app.models.oltp.user import User
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
def list_my_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    """Joriy user uchun xabarlar."""
    result = notification_service.list_user_notifications(db, user.id, unread_only, limit)
    return {
        "total_unread": result["total_unread"],
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "link": n.link,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in result["items"]
        ],
    }


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    if not notification_service.mark_read(db, notification_id, user.id):
        raise HTTPException(404, "Xabar topilmadi")
    return {"success": True}


@router.post("/mark-all-read")
def mark_all_as_read(
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    count = notification_service.mark_all_read(db, user.id)
    return {"success": True, "marked": count}
