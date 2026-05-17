"""Notification servisi — in-app va email."""
import smtplib
from datetime import datetime
from email.message import EmailMessage

from loguru import logger
from sqlalchemy.orm import Session

from app.config import settings
from app.models.oltp.notification import Notification
from app.models.oltp.user import User


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info",
    link: str | None = None,
    send_email: bool = False,
) -> Notification:
    """Yangi in-app notification yaratish va ixtiyoriy email yuborish."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    if send_email:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            try:
                send_email_notification(user.email, title, message)
            except Exception as e:
                logger.warning("Email yuborishda xato: {}", e)

    return notif


def send_email_notification(to_email: str, subject: str, body: str) -> None:
    """Email yuborish (SMTP).

    Konfiguratsiya .env da bo'lishi kerak:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
    """
    smtp_host = getattr(settings, "smtp_host", None)
    if not smtp_host:
        logger.debug("SMTP sozlanmagan — email yuborilmadi")
        return

    msg = EmailMessage()
    msg["From"] = getattr(settings, "smtp_from", "noreply@university.uz")
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, getattr(settings, "smtp_port", 587)) as smtp:
        smtp.starttls()
        user = getattr(settings, "smtp_user", None)
        if user:
            smtp.login(user, getattr(settings, "smtp_password", ""))
        smtp.send_message(msg)


def list_user_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    limit: int = 50,
):
    q = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        q = q.filter(Notification.is_read == False)  # noqa: E712
    total_unread = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .count()
    )
    items = q.order_by(Notification.created_at.desc()).limit(limit).all()
    return {"items": items, "total_unread": total_unread}


def mark_read(db: Session, notification_id: int, user_id: int) -> bool:
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if not notif:
        return False
    notif.is_read = True
    notif.read_at = datetime.utcnow()
    db.commit()
    return True


def mark_all_read(db: Session, user_id: int) -> int:
    count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .update({Notification.is_read: True, Notification.read_at: datetime.utcnow()})
    )
    db.commit()
    return count


def notify_low_gpa(db: Session, student_id: int, gpa: float) -> None:
    """Past GPA uchun ogohlantirish — talaba o'ziga va dekanga."""
    from app.models.oltp.student import Student
    from app.models.oltp.user import UserRole

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student or not student.user_id:
        return

    create_notification(
        db,
        user_id=student.user_id,
        title="GPA past darajada",
        message=f"Joriy GPA: {gpa:.2f}. Akademik xavf zonasida. Dekanat bilan bog'laning.",
        notification_type="warning",
        link="/dashboard",
        send_email=True,
    )

    # Dekanlarga ham xabar
    deans = db.query(User).filter(User.role == UserRole.DEKAN).all()
    for dean in deans:
        create_notification(
            db,
            user_id=dean.id,
            title="Xavf zonasidagi talaba",
            message=f"{student.full_name} ({student.student_id}) — GPA {gpa:.2f}",
            notification_type="warning",
            link=f"/students/{student.id}",
        )


def notify_grade_added(db: Session, student_id: int, subject_name: str, grade_value: float) -> None:
    """Talaba uchun yangi baho kiritilganida xabar."""
    from app.models.oltp.student import Student

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student or not student.user_id:
        return

    create_notification(
        db,
        user_id=student.user_id,
        title="Yangi baho",
        message=f"{subject_name}: {grade_value} ball",
        notification_type="success" if grade_value >= 55 else "warning",
        link="/dashboard",
    )
