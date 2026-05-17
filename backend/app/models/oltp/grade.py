"""Baholar modeli (OLTP)."""
from datetime import date, datetime
from typing import List

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import OLTPBase


class AssessmentType(OLTPBase):
    __tablename__ = "assessment_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(256))
    weight_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=25.0)

    grades: Mapped[List["Grade"]] = relationship(back_populates="assessment_type")


class Grade(OLTPBase):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), index=True)
    assessment_type_id: Mapped[int] = mapped_column(ForeignKey("assessment_types.id"))

    grade_value: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    attendance_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=100.0)
    is_passed: Mapped[bool] = mapped_column(Boolean, default=True)

    semester: Mapped[str] = mapped_column(String(16), nullable=False)  # "kuzgi" yoki "bahorgi"
    academic_year: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # 2024-2025
    grade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    student: Mapped["Student"] = relationship(back_populates="grades")  # type: ignore # noqa
    subject: Mapped["Subject"] = relationship(back_populates="grades")  # type: ignore # noqa
    teacher: Mapped["Teacher"] = relationship(back_populates="grades")  # type: ignore # noqa
    assessment_type: Mapped["AssessmentType"] = relationship(back_populates="grades")
