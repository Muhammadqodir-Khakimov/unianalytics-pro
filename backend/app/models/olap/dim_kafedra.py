"""DIMENSION: Kafedra o'lchovi (fakultet ostidagi tashkiliy birlik).

TZ 6.2.2 — DIM_KAFEDRA. Star schemada dim_faculty bilan birga
tahliliy kesimlarni aniqlashtirish uchun.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase


class DimKafedra(OLAPBase):
    __tablename__ = "dim_kafedra"
    __table_args__ = (
        Index("ix_dim_kafedra_kod", "kafedra_kodi"),
        Index("ix_dim_kafedra_fakultet", "faculty_key"),
    )

    kafedra_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kafedra_kodi: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    kafedra_nomi: Mapped[str] = mapped_column(String(200), nullable=False)
    faculty_key: Mapped[int] = mapped_column(ForeignKey("dim_faculty.faculty_key"), nullable=False)
    mudir_fish: Mapped[str | None] = mapped_column(String(200))
    loaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
