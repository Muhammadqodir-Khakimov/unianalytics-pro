"""Ariza tizimi: talaba ariza yuboradi, dekan ko'rib chiqadi."""
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


class ApplicationType(str, Enum):
    EXAM_RETAKE = "exam_retake"  # Qayta topshirish
    ACADEMIC_LEAVE = "academic_leave"  # Akademik ta'til
    SUBJECT_CHANGE = "subject_change"  # Fan almashtirish
    TRANSFER = "transfer"  # Guruh/yo'nalish almashtirish
    CERTIFICATE = "certificate"  # Ma'lumotnoma so'rash
    OTHER = "other"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Application(OLTPBase):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)

    application_type: Mapped[ApplicationType] = mapped_column(
        SAEnum(ApplicationType, name="application_type"), index=True
    )
    subject: Mapped[str] = mapped_column(String(256))  # arizaning sarlavhasi
    body: Mapped[str] = mapped_column(Text)  # tafsilot

    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.PENDING,
        index=True,
    )
    response: Mapped[str | None] = mapped_column(Text)  # dekan javobi
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
