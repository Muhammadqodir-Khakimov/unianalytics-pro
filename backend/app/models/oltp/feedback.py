"""TeacherFeedback va sentiment modellari (Sprint 6.2)."""
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


class FeedbackCategory(str, Enum):
    TEACHING_QUALITY = "teaching_quality"
    KNOWLEDGE = "knowledge"
    ATTITUDE = "attitude"
    FAIRNESS = "fairness"
    AVAILABILITY = "availability"


class TeacherFeedback(OLTPBase):
    """Anonim talaba fikr-mulohazasi (o'qituvchi haqida).

    student_id saqlanmaydi — faqat anonymous_id (hash).
    """

    __tablename__ = "teacher_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), index=True)
    subject_id: Mapped[int | None] = mapped_column(ForeignKey("subjects.id"))
    semester: Mapped[str] = mapped_column(String(16))
    academic_year: Mapped[str] = mapped_column(String(16))

    # Anonim — talabaning student_id ni hash qilamiz
    anonymous_id: Mapped[str] = mapped_column(String(64), index=True)

    # Ratings (1-5)
    rating_teaching: Mapped[int] = mapped_column(Integer)  # o'qitish sifati
    rating_knowledge: Mapped[int] = mapped_column(Integer)  # bilim chuqurligi
    rating_attitude: Mapped[int] = mapped_column(Integer)  # munosabat
    rating_fairness: Mapped[int] = mapped_column(Integer)  # adolatlik
    rating_availability: Mapped[int] = mapped_column(Integer)  # mavjudlik
    rating_overall: Mapped[float] = mapped_column(Numeric(3, 2))

    # Erkin matn
    comment: Mapped[str | None] = mapped_column(Text)

    # Sentiment analysis natijasi
    sentiment_label: Mapped[str | None] = mapped_column(String(16))  # positive/negative/neutral
    sentiment_score: Mapped[float | None] = mapped_column(Numeric(4, 3))  # -1.0 .. +1.0
    toxicity_flag: Mapped[bool] = mapped_column(default=False)

    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
