"""DIMENSION: Guruh o'lchovi (talabalar akademik guruhlari).

TZ 6.2.2 — DIM_GURUH. Star schemada talaba va kafedra darajalari
o'rtasidagi alohida agregatsiya kesimi.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase


class DimGroup(OLAPBase):
    __tablename__ = "dim_group"
    __table_args__ = (
        Index("ix_dim_group_kod", "guruh_kodi"),
        Index("ix_dim_group_kafedra", "kafedra_key"),
        Index("ix_dim_group_kurs", "kurs"),
    )

    group_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guruh_kodi: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    guruh_nomi: Mapped[str] = mapped_column(String(50), nullable=False)
    kurs: Mapped[int] = mapped_column(Integer, nullable=False)
    kafedra_key: Mapped[int] = mapped_column(ForeignKey("dim_kafedra.kafedra_key"), nullable=False)
    talabalar_soni: Mapped[int] = mapped_column(Integer, default=0)
    faol: Mapped[bool] = mapped_column(Boolean, default=True)
    loaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
