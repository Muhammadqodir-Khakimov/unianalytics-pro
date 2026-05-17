"""DIMENSION: Talaba o'lchovi."""
from datetime import date, datetime

from sqlalchemy import CHAR, Date, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase


class DimStudent(OLAPBase):
    __tablename__ = "dim_student"
    __table_args__ = (
        Index("ix_dim_student_id", "student_id"),
        Index("ix_dim_student_group", "group_name"),
    )

    student_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(32), nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    gender: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date)
    enrollment_year: Mapped[int] = mapped_column(nullable=False)
    group_name: Mapped[str] = mapped_column(String(64), nullable=False)
    education_form: Mapped[str] = mapped_column(String(16), default="kunduzgi")
    status: Mapped[str] = mapped_column(String(32), default="faol")
    loaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
