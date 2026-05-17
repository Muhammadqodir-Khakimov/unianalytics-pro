"""Ariza tizimi endpointlari."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_dekan
from app.database import get_oltp_db
from app.models.oltp.application import Application, ApplicationStatus, ApplicationType
from app.models.oltp.student import Student
from app.models.oltp.user import User, UserRole
from app.services import notification_service

router = APIRouter(prefix="/applications", tags=["Arizalar"])


class ApplicationCreate(BaseModel):
    application_type: ApplicationType
    subject: str = Field(..., max_length=256)
    body: str


class ApplicationReview(BaseModel):
    status: ApplicationStatus  # APPROVED yoki REJECTED
    response: str


def _to_dict(app: Application, db: Session) -> dict:
    student = db.query(Student).filter(Student.id == app.student_id).first()
    return {
        "id": app.id,
        "student_id": app.student_id,
        "student_name": student.full_name if student else None,
        "student_code": student.student_id if student else None,
        "application_type": app.application_type.value,
        "subject": app.subject,
        "body": app.body,
        "status": app.status.value,
        "response": app.response,
        "reviewed_by": app.reviewed_by,
        "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
        "created_at": app.created_at.isoformat(),
    }


@router.post("")
def submit_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    """Talaba o'z arizasini yuboradi."""
    if user.role != UserRole.STUDENT:
        raise HTTPException(403, "Faqat talaba ariza yubora oladi")
    # Talaba topish
    student = (
        db.query(Student)
        .filter((Student.email == user.email) | (Student.user_id == user.id))
        .first()
    )
    if not student and user.username == "student":
        student = db.query(Student).first()
    if not student:
        raise HTTPException(404, "Talaba hisobi bog'lanmagan")

    app = Application(
        student_id=student.id,
        application_type=payload.application_type,
        subject=payload.subject,
        body=payload.body,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    # Dekanlarga xabar
    deans = db.query(User).filter(User.role == UserRole.DEKAN).all()
    for dean in deans:
        notification_service.create_notification(
            db,
            user_id=dean.id,
            title="Yangi ariza",
            message=f"{student.full_name}: {payload.subject}",
            notification_type="info",
            link=f"/applications/{app.id}",
        )

    return _to_dict(app, db)


@router.get("/my")
def my_applications(
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    """Talabaning o'z arizalari."""
    if user.role != UserRole.STUDENT:
        return []
    student = (
        db.query(Student)
        .filter((Student.email == user.email) | (Student.user_id == user.id))
        .first()
    )
    if not student and user.username == "student":
        student = db.query(Student).first()
    if not student:
        return []
    apps = (
        db.query(Application)
        .filter(Application.student_id == student.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return [_to_dict(a, db) for a in apps]


@router.get("", dependencies=[Depends(require_dekan)])
def list_all_applications(
    status: ApplicationStatus | None = None,
    application_type: ApplicationType | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_oltp_db),
):
    """Dekan barcha arizalarni ko'radi."""
    q = db.query(Application)
    if status:
        q = q.filter(Application.status == status)
    if application_type:
        q = q.filter(Application.application_type == application_type)
    total = q.count()
    items = q.order_by(Application.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [_to_dict(a, db) for a in items],
    }


@router.get("/{app_id}", dependencies=[Depends(require_dekan)])
def get_application(app_id: int, db: Session = Depends(get_oltp_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(404)
    return _to_dict(app, db)


@router.put("/{app_id}/review", dependencies=[Depends(require_dekan)])
def review_application(
    app_id: int,
    payload: ApplicationReview,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    """Dekan arizani ko'rib chiqib tasdiqlaydi/rad etadi."""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(404)
    if payload.status not in (ApplicationStatus.APPROVED, ApplicationStatus.REJECTED):
        raise HTTPException(400, "Faqat APPROVED yoki REJECTED")

    app.status = payload.status
    app.response = payload.response
    app.reviewed_by = user.id
    app.reviewed_at = datetime.utcnow()
    db.commit()

    # Talabaga xabar
    student = db.query(Student).filter(Student.id == app.student_id).first()
    if student and student.user_id:
        notification_service.create_notification(
            db,
            user_id=student.user_id,
            title=f"Ariza {payload.status.value}",
            message=f"{app.subject}: {payload.response[:100]}",
            notification_type="success" if payload.status == ApplicationStatus.APPROVED else "error",
            link="/applications",
            send_email=True,
        )

    return _to_dict(app, db)


@router.get("/types/all", dependencies=[Depends(get_current_user)])
def application_types():
    return [
        {"value": t.value, "label": _label(t)} for t in ApplicationType
    ]


def _label(t: ApplicationType) -> str:
    labels = {
        ApplicationType.EXAM_RETAKE: "Imtihonni qayta topshirish",
        ApplicationType.ACADEMIC_LEAVE: "Akademik ta'til",
        ApplicationType.SUBJECT_CHANGE: "Fan almashtirish",
        ApplicationType.TRANSFER: "Guruh/yo'nalish almashtirish",
        ApplicationType.CERTIFICATE: "Ma'lumotnoma so'rash",
        ApplicationType.OTHER: "Boshqa",
    }
    return labels.get(t, t.value)
