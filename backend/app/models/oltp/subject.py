"""Fan modeli (OLTP)."""
from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import DateTime, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import OLTPBase


class SubjectType(str, Enum):
    MAJBURIY = "majburiy"
    TANLOV = "tanlov"


class Subject(OLTPBase):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    department: Mapped[str | None] = mapped_column(String(256))
    credit_hours: Mapped[int] = mapped_column(Integer, default=3)
    subject_type: Mapped[SubjectType] = mapped_column(
        SAEnum(SubjectType, name="subject_type"),
        default=SubjectType.MAJBURIY,
    )
    semester: Mapped[int] = mapped_column(Integer, default=1)
    description: Mapped[str | None] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    grades: Mapped[List["Grade"]] = relationship(back_populates="subject")  # type: ignore # noqa
