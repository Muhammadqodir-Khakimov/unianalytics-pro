"""Jadval (timetable) va davomat (attendance) modellari."""
from datetime import date, datetime, time
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


class LessonType(str, Enum):
    LECTURE = "lecture"
    SEMINAR = "seminar"
    LAB = "lab"
    PRACTICE = "practice"


class ScheduleEntry(OLTPBase):
    """Haftalik jadval yozuvi: dushanba 09:00 da X guruh Y fani."""

    __tablename__ = "schedule_entries"
    __table_args__ = (
        UniqueConstraint("group_id", "weekday", "start_time", "academic_year", "semester",
                         name="uq_schedule_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))

    weekday: Mapped[int] = mapped_column(Integer)  # 1=Dush, 7=Yak
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    room: Mapped[str | None] = mapped_column(String(64))
    lesson_type: Mapped[LessonType] = mapped_column(
        SAEnum(LessonType, name="lesson_type"), default=LessonType.LECTURE
    )

    academic_year: Mapped[str] = mapped_column(String(16), index=True)
    semester: Mapped[str] = mapped_column(String(16), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AttendanceRecord(OLTPBase):
    """Har dars uchun har talaba davomati."""

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("schedule_id", "student_id", "lesson_date", name="uq_attendance"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedule_entries.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    lesson_date: Mapped[date] = mapped_column(Date, index=True)

    status: Mapped[AttendanceStatus] = mapped_column(
        SAEnum(AttendanceStatus, name="attendance_status"), default=AttendanceStatus.PRESENT
    )
    note: Mapped[str | None] = mapped_column(String(256))
    marked_by: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"))
    marked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
