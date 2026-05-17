"""Ota-ona ↔ talaba bog'lanishi va dayjest sozlamalari (TZ 4.2.4).

JSON-fayl bilan saqlash o'rniga production uchun OLTP jadvallar.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import OLTPBase


class ParentLinkStatus(str, Enum):
    PENDING = "pending"      # so'rov yuborildi, talaba tasdig'i kutilmoqda
    APPROVED = "approved"    # talaba tasdiqladi
    REJECTED = "rejected"    # talaba rad etdi
    REVOKED = "revoked"      # keyinroq bekor qilindi


class ParentLink(OLTPBase):
    """Ota-ona <-> talaba bog'lanishi.

    Bir ota-ona bir nechta farzandga bog'lanishi mumkin (TZ 4.2.4 — Ota-ona
    uchun maxsus funksiyalar). Bitta ota-ona+talaba juftligi yagona bo'ladi.
    """

    __tablename__ = "parent_links"
    __table_args__ = (
        UniqueConstraint("parent_user_id", "student_id", name="uq_parent_student"),
        Index("ix_parent_link_status", "status"),
        Index("ix_parent_link_student", "student_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ParentLinkStatus] = mapped_column(
        SAEnum(ParentLinkStatus, name="parent_link_status"),
        default=ParentLinkStatus.PENDING,
        nullable=False,
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime)
    decided_by_student: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str | None] = mapped_column(String(256))

    parent: Mapped["User"] = relationship(  # type: ignore[name-defined] # noqa: F821
        "User", foreign_keys=[parent_user_id]
    )
    student: Mapped["Student"] = relationship(  # type: ignore[name-defined] # noqa: F821
        "Student", foreign_keys=[student_id]
    )


class UserPreferences(OLTPBase):
    """Foydalanuvchi sozlamalari (bildirishnoma, dayjest, til).

    User 1↔1 munosabati — keyingi versiyalarda kengaytirish uchun
    `User` ga ustun qo'shish o'rniga alohida jadval ajratildi.
    """

    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # TZ 4.2.4 — haftalik dayjest (juma 18:00)
    weekly_digest_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # TZ 4.2.4 — yangi baho push xabarnomasi
    notify_new_grade: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # TZ 4.2.4 — akademik xavf signali
    notify_academic_risk: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # TZ 4.7 — interfeys tili
    language: Mapped[str] = mapped_column(String(8), default="uz_lat", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", uselist=False)  # type: ignore[name-defined] # noqa: F821
