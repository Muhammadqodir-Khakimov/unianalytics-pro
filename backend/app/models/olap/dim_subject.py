"""DIMENSION: Fan o'lchovi."""
from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase


class DimSubject(OLAPBase):
    __tablename__ = "dim_subject"
    __table_args__ = (
        Index("ix_dim_subject_code", "subject_code"),
        Index("ix_dim_subject_dept", "department"),
    )

    subject_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_code: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_name: Mapped[str] = mapped_column(String(256), nullable=False)
    department: Mapped[str | None] = mapped_column(String(256))
    credit_hours: Mapped[int] = mapped_column(default=3)
    subject_type: Mapped[str] = mapped_column(String(16), default="majburiy")
    semester: Mapped[int] = mapped_column(default=1)
    loaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
