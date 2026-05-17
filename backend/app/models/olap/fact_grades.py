"""FACT: Talabalar baholari (markaziy fakt jadval)."""
from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLAPBase

# SQLite da BigInteger AUTOINCREMENT ishlamaydi; Integer ga variant qilamiz.
PKBigInt = BigInteger().with_variant(Integer(), "sqlite")


class FactStudentGrade(OLAPBase):
    """Star Schema markazi — har bir baho yozuvi.

    OLAP querylar uchun composite indekslar bilan optimallashtirilgan.
    """

    __tablename__ = "fact_student_grades"
    __table_args__ = (
        Index("ix_fact_student_key", "student_key"),
        Index("ix_fact_subject_key", "subject_key"),
        Index("ix_fact_time_key", "time_key"),
        Index("ix_fact_faculty_key", "faculty_key"),
        Index("ix_fact_faculty_time", "faculty_key", "time_key"),
        Index("ix_fact_student_time", "student_key", "time_key"),
    )

    grade_id: Mapped[int] = mapped_column(PKBigInt, primary_key=True, autoincrement=True)

    # Foreign keys (dimension lar uchun)
    student_key: Mapped[int] = mapped_column(ForeignKey("dim_student.student_key"), nullable=False)
    subject_key: Mapped[int] = mapped_column(ForeignKey("dim_subject.subject_key"), nullable=False)
    teacher_key: Mapped[int] = mapped_column(ForeignKey("dim_teacher.teacher_key"), nullable=False)
    time_key: Mapped[int] = mapped_column(ForeignKey("dim_time.time_key"), nullable=False)
    faculty_key: Mapped[int] = mapped_column(ForeignKey("dim_faculty.faculty_key"), nullable=False)
    assessment_type_key: Mapped[int] = mapped_column(
        ForeignKey("dim_assessment_type.assessment_type_key"), nullable=False
    )

    # Measures (o'lchamlar)
    grade_value: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    credit_hours: Mapped[int] = mapped_column(Integer, default=3)
    attendance_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=100.0)
    gpa_points: Mapped[float] = mapped_column(Numeric(3, 2), default=0.0)
    is_passed: Mapped[bool] = mapped_column(Boolean, default=True)
