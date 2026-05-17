"""Jadval (timetable) va davomat (attendance) endpointlari."""
from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_any, require_teacher
from app.database import get_oltp_db
from app.models.oltp.schedule import (
    AttendanceRecord,
    AttendanceStatus,
    ScheduleEntry,
)
from app.models.oltp.student import Student
from app.models.oltp.subject import Subject
from app.models.oltp.teacher import Teacher
from app.models.oltp.faculty import Group
from app.schemas.schedule import (
    AttendanceBulkMark,
    ScheduleCreate,
    ScheduleResponse,
)

router = APIRouter(prefix="/schedule", tags=["Jadval va davomat"])

WEEKDAY_NAMES = ["", "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]


def _enrich(entry: ScheduleEntry, db: Session) -> dict:
    """Schedule entry ga JOIN ma'lumotlarini qo'shish."""
    subj = db.query(Subject).filter(Subject.id == entry.subject_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == entry.teacher_id).first()
    group = db.query(Group).filter(Group.id == entry.group_id).first()
    return {
        "id": entry.id,
        "group_id": entry.group_id,
        "subject_id": entry.subject_id,
        "teacher_id": entry.teacher_id,
        "weekday": entry.weekday,
        "weekday_name": WEEKDAY_NAMES[entry.weekday] if 1 <= entry.weekday <= 7 else "",
        "start_time": entry.start_time.isoformat() if entry.start_time else None,
        "end_time": entry.end_time.isoformat() if entry.end_time else None,
        "room": entry.room,
        "lesson_type": entry.lesson_type.value,
        "academic_year": entry.academic_year,
        "semester": entry.semester,
        "is_active": entry.is_active,
        "subject_name": subj.name if subj else None,
        "subject_code": subj.code if subj else None,
        "teacher_name": teacher.full_name if teacher else None,
        "group_name": group.name if group else None,
    }


@router.get("", dependencies=[Depends(require_any)])
def list_schedule(
    group_id: int | None = None,
    teacher_id: int | None = None,
    academic_year: str | None = None,
    semester: str | None = None,
    db: Session = Depends(get_oltp_db),
):
    """Jadval ro'yxati (filtr bilan)."""
    q = db.query(ScheduleEntry).filter(ScheduleEntry.is_active == True)  # noqa: E712
    if group_id:
        q = q.filter(ScheduleEntry.group_id == group_id)
    if teacher_id:
        q = q.filter(ScheduleEntry.teacher_id == teacher_id)
    if academic_year:
        q = q.filter(ScheduleEntry.academic_year == academic_year)
    if semester:
        q = q.filter(ScheduleEntry.semester == semester)

    entries = q.order_by(ScheduleEntry.weekday, ScheduleEntry.start_time).all()
    return [_enrich(e, db) for e in entries]


@router.get("/my", dependencies=[Depends(require_any)])
def my_schedule(
    user_id: int | None = None,
    db: Session = Depends(get_oltp_db),
):
    """Joriy foydalanuvchi rolga qarab o'z jadvalini ko'radi.

    Note: keyinroq get_current_user bilan to'g'rilanadi
    """
    # Placeholder — frontend rolga qarab boshqasini chaqirsin
    return {"message": "Use /schedule with appropriate filters"}


@router.post(
    "",
    response_model=dict,
    dependencies=[Depends(require_teacher)],
)
def create_schedule(payload: ScheduleCreate, db: Session = Depends(get_oltp_db)):
    """Yangi jadval yozuvi qo'shish."""
    entry = ScheduleEntry(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _enrich(entry, db)


@router.delete("/{schedule_id}", dependencies=[Depends(require_teacher)])
def delete_schedule(schedule_id: int, db: Session = Depends(get_oltp_db)):
    e = db.query(ScheduleEntry).filter(ScheduleEntry.id == schedule_id).first()
    if not e:
        raise HTTPException(404, "Topilmadi")
    db.delete(e)
    db.commit()
    return {"success": True}


# ============================================================
# Davomat endpointlari
# ============================================================


@router.post("/attendance/bulk", dependencies=[Depends(require_teacher)])
def mark_attendance(payload: AttendanceBulkMark, db: Session = Depends(get_oltp_db)):
    """Bir darsda hamma talabalar davomatini birga belgilash."""
    schedule = db.query(ScheduleEntry).filter(ScheduleEntry.id == payload.schedule_id).first()
    if not schedule:
        raise HTTPException(404, "Jadval topilmadi")

    saved = 0
    for mark in payload.marks:
        existing = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.schedule_id == payload.schedule_id,
                AttendanceRecord.student_id == mark.student_id,
                AttendanceRecord.lesson_date == payload.lesson_date,
            )
            .first()
        )
        if existing:
            existing.status = mark.status
            existing.note = mark.note
        else:
            db.add(
                AttendanceRecord(
                    schedule_id=payload.schedule_id,
                    student_id=mark.student_id,
                    lesson_date=payload.lesson_date,
                    status=mark.status,
                    note=mark.note,
                    marked_by=schedule.teacher_id,
                )
            )
        saved += 1
    db.commit()
    return {"saved": saved}


@router.get("/attendance", dependencies=[Depends(require_any)])
def list_attendance(
    schedule_id: int | None = None,
    student_id: int | None = None,
    lesson_date: date_type | None = None,
    db: Session = Depends(get_oltp_db),
):
    """Davomat yozuvlari."""
    q = db.query(AttendanceRecord)
    if schedule_id:
        q = q.filter(AttendanceRecord.schedule_id == schedule_id)
    if student_id:
        q = q.filter(AttendanceRecord.student_id == student_id)
    if lesson_date:
        q = q.filter(AttendanceRecord.lesson_date == lesson_date)
    records = q.order_by(AttendanceRecord.lesson_date.desc()).limit(500).all()
    return [
        {
            "id": r.id,
            "schedule_id": r.schedule_id,
            "student_id": r.student_id,
            "lesson_date": r.lesson_date.isoformat(),
            "status": r.status.value,
            "note": r.note,
            "marked_at": r.marked_at.isoformat(),
        }
        for r in records
    ]


@router.get("/attendance/student/{student_id}/stats", dependencies=[Depends(require_any)])
def student_attendance_stats(student_id: int, db: Session = Depends(get_oltp_db)):
    """Talaba davomati statistikasi."""
    all_records = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student_id).all()
    total = len(all_records)
    present = sum(1 for r in all_records if r.status == AttendanceStatus.PRESENT)
    absent = sum(1 for r in all_records if r.status == AttendanceStatus.ABSENT)
    late = sum(1 for r in all_records if r.status == AttendanceStatus.LATE)
    excused = sum(1 for r in all_records if r.status == AttendanceStatus.EXCUSED)
    return {
        "total_lessons": total,
        "present": present,
        "absent": absent,
        "late": late,
        "excused": excused,
        "attendance_percentage": round(present * 100.0 / total, 2) if total > 0 else 100.0,
    }
