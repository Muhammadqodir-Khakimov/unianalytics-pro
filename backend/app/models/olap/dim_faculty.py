"""DIMENSION: Fakultet o'lchovi (ierarxik)."""
from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase


class DimFaculty(OLAPBase):
    __tablename__ = "dim_faculty"
    __table_args__ = (
        Index("ix_dim_faculty_name", "faculty_name"),
        Index("ix_dim_faculty_group", "group_name"),
    )

    faculty_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    faculty_name: Mapped[str] = mapped_column(String(256), nullable=False)
    department: Mapped[str | None] = mapped_column(String(256))
    specialty: Mapped[str] = mapped_column(String(256), nullable=False)
    course: Mapped[int] = mapped_column(nullable=False)
    group_name: Mapped[str] = mapped_column(String(64), nullable=False)
    loaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
