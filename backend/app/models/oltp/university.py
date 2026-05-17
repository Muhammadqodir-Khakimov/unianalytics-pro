"""University va Department modellari (to'liq akademik ierarxiya).

Ierarxiya: University → Faculty → Department → Specialty → Group → Student
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


class University(OLTPBase):
    """Universitet — Tenant ga teng (multi-tenant ichida 1 ta universitet).

    Ammo bitta tenant ichida bir necha universitet bo'lishi mumkin (masalan vazirlik).
    """

    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int | None] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    short_name: Mapped[str] = mapped_column(String(64))
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    hemis_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)

    rector_name: Mapped[str | None] = mapped_column(String(256))
    rector_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    address: Mapped[str | None] = mapped_column(String(512))
    region: Mapped[str | None] = mapped_column(String(128))
    city: Mapped[str | None] = mapped_column(String(128))
    phone: Mapped[str | None] = mapped_column(String(64))
    email: Mapped[str | None] = mapped_column(String(128))
    website: Mapped[str | None] = mapped_column(String(256))

    # Coordinates for map
    latitude: Mapped[float | None] = mapped_column()
    longitude: Mapped[float | None] = mapped_column()

    # Type
    university_type: Mapped[str] = mapped_column(String(32), default="state")  # state/private/branch

    student_count: Mapped[int] = mapped_column(Integer, default=0)
    founded_year: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Department(OLTPBase):
    """Kafedra — Faculty ichida joylashadi.

    Faculty → Department → Specialty bog'liqlik.
    """

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    code: Mapped[str] = mapped_column(String(32))
    head_teacher_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"))
    description: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
