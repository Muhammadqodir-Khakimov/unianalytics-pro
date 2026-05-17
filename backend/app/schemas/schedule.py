"""Jadval va davomat sxemalari."""
from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.models.oltp.schedule import AttendanceStatus, LessonType


class ScheduleCreate(BaseModel):
    group_id: int
    subject_id: int
    teacher_id: int
    weekday: int = Field(..., ge=1, le=7)
    start_time: time
    end_time: time
    room: str | None = None
    lesson_type: LessonType = LessonType.LECTURE
    academic_year: str
    semester: str


class ScheduleResponse(BaseModel):
    id: int
    group_id: int
    subject_id: int
    teacher_id: int
    weekday: int
    start_time: time
    end_time: time
    room: str | None
    lesson_type: LessonType
    academic_year: str
    semester: str
    is_active: bool
    # Bonus — JOIN qilingan ma'lumot
    subject_name: str | None = None
    teacher_name: str | None = None
    group_name: str | None = None

    model_config = {"from_attributes": True}


class AttendanceMark(BaseModel):
    student_id: int
    status: AttendanceStatus
    note: str | None = None


class AttendanceBulkMark(BaseModel):
    schedule_id: int
    lesson_date: date
    marks: list[AttendanceMark]


class AttendanceResponse(BaseModel):
    id: int
    schedule_id: int
    student_id: int
    lesson_date: date
    status: AttendanceStatus
    note: str | None
    marked_at: datetime

    model_config = {"from_attributes": True}
