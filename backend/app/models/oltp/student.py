"""Talaba modeli (OLTP)."""
from datetime import date, datetime
from enum import Enum
from typing import List

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import OLTPBase


class EducationForm(str, Enum):
    KUNDUZGI = "kunduzgi"
    SIRTQI = "sirtqi"
    KECHKI = "kechki"


class StudentStatus(str, Enum):
    FAOL = "faol"
    AKADEMIK_TATIL = "akademik_tatil"
    CHETLATILGAN = "chetlatilgan"
    BITIRGAN = "bitirgan"


class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"


class Student(OLTPBase):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    gender: Mapped[Gender] = mapped_column(SAEnum(Gender, name="gender"), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(128))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    education_form: Mapped[EducationForm] = mapped_column(
        SAEnum(EducationForm, name="education_form"),
        default=EducationForm.KUNDUZGI,
    )
    status: Mapped[StudentStatus] = mapped_column(
        SAEnum(StudentStatus, name="student_status"),
        default=StudentStatus.FAOL,
    )
    enrollment_year: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    group: Mapped["Group"] = relationship(back_populates="students")  # type: ignore # noqa
    grades: Mapped[List["Grade"]] = relationship(back_populates="student")  # type: ignore # noqa
