"""O'qituvchi modeli (OLTP)."""
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import OLTPBase


class Teacher(OLTPBase):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    academic_degree: Mapped[str | None] = mapped_column(String(64))
    position: Mapped[str | None] = mapped_column(String(128))
    department: Mapped[str | None] = mapped_column(String(256))
    phone: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(128))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    grades: Mapped[List["Grade"]] = relationship(back_populates="teacher")  # type: ignore # noqa
