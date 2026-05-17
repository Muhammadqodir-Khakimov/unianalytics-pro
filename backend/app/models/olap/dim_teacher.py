"""DIMENSION: O'qituvchi o'lchovi."""
from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase


class DimTeacher(OLAPBase):
    __tablename__ = "dim_teacher"
    __table_args__ = (Index("ix_dim_teacher_id", "teacher_id"),)

    teacher_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[str] = mapped_column(String(32), nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    academic_degree: Mapped[str | None] = mapped_column(String(64))
    position: Mapped[str | None] = mapped_column(String(128))
    department: Mapped[str | None] = mapped_column(String(256))
    loaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
