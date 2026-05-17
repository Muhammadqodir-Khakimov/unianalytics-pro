"""DIMENSION: Baholash turi o'lchovi."""
from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase


class DimAssessmentType(OLAPBase):
    __tablename__ = "dim_assessment_type"

    assessment_type_key: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    weight_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=25.0)
    description: Mapped[str | None] = mapped_column(String(256))
