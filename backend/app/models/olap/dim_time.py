"""DIMENSION: Vaqt o'lchovi (ierarxik)."""
from datetime import date

from sqlalchemy import Date, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase


class DimTime(OLAPBase):
    __tablename__ = "dim_time"
    __table_args__ = (
        Index("ix_dim_time_year", "year"),
        Index("ix_dim_time_academic_year", "academic_year"),
        Index("ix_dim_time_semester", "semester"),
    )

    time_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    day: Mapped[int] = mapped_column(nullable=False)
    week: Mapped[int] = mapped_column(nullable=False)
    month: Mapped[int] = mapped_column(nullable=False)
    month_name: Mapped[str] = mapped_column(String(16), nullable=False)
    quarter: Mapped[int] = mapped_column(nullable=False)
    semester: Mapped[str] = mapped_column(String(16), nullable=False)  # kuzgi/bahorgi
    academic_year: Mapped[str] = mapped_column(String(16), nullable=False)  # 2024-2025
    year: Mapped[int] = mapped_column(nullable=False)
