"""Audit log modeli — tizimda yuz bergan har bir muhim amal qayd qilinadi."""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


class AuditLog(OLTPBase):
    """Universal audit log — kim, qachon, qaysi resursda, nima qilgan."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, index=True)
    username: Mapped[str | None] = mapped_column(String(64), index=True)
    user_role: Mapped[str | None] = mapped_column(String(32))

    action: Mapped[str] = mapped_column(String(32), index=True)  # CREATE/UPDATE/DELETE/LOGIN/EXPORT
    resource_type: Mapped[str] = mapped_column(String(64), index=True)  # student, grade, etc
    resource_id: Mapped[str | None] = mapped_column(String(64))

    description: Mapped[str | None] = mapped_column(String(512))
    changes_json: Mapped[str | None] = mapped_column(Text)  # eski/yangi qiymatlar JSON

    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(512))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
