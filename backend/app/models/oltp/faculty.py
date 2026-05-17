"""Fakultet, yo'nalish va guruh modellari (OLTP)."""
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import OLTPBase


class Faculty(OLTPBase):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    specialties: Mapped[List["Specialty"]] = relationship(back_populates="faculty", cascade="all, delete")


class Specialty(OLTPBase):
    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id", ondelete="CASCADE"))

    faculty: Mapped["Faculty"] = relationship(back_populates="specialties")
    groups: Mapped[List["Group"]] = relationship(back_populates="specialty", cascade="all, delete")


class Group(OLTPBase):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    course: Mapped[int] = mapped_column(Integer, nullable=False)
    specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id", ondelete="CASCADE"))
    enrollment_year: Mapped[int] = mapped_column(Integer, nullable=False)

    specialty: Mapped["Specialty"] = relationship(back_populates="groups")
    students: Mapped[List["Student"]] = relationship(back_populates="group")  # type: ignore # noqa
