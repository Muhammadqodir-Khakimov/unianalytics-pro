"""ETL servisi — OLTP databazadan OLAP star schema ga ko'chirish.

Jarayon:
1. EXTRACT — OLTP dan yangi/o'zgargan yozuvlarni o'qish
2. TRANSFORM — dimension keylarini topish/yaratish, denormalizatsiya
3. LOAD — fact va dimension jadvallarni to'ldirish
"""
from datetime import date, datetime
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import olap_session, oltp_session
from app.models.olap.dim_assessment import DimAssessmentType
from app.models.olap.dim_faculty import DimFaculty
from app.models.olap.dim_student import DimStudent
from app.models.olap.dim_subject import DimSubject
from app.models.olap.dim_teacher import DimTeacher
from app.models.olap.dim_time import DimTime
from app.models.olap.fact_grades import FactStudentGrade
from app.models.oltp.faculty import Group
from app.models.oltp.grade import AssessmentType, Grade
from app.models.oltp.student import Student
from app.models.oltp.subject import Subject
from app.models.oltp.teacher import Teacher


def _get_month_name(month: int) -> str:
    names = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr",
    ]
    return names[month - 1]


def _academic_year_from_date(d: date) -> str:
    """Sentyabrdan boshlab yangi o'quv yili."""
    if d.month >= 9:
        return f"{d.year}-{d.year + 1}"
    return f"{d.year - 1}-{d.year}"


def _semester_from_date(d: date) -> str:
    return "kuzgi" if d.month >= 9 or d.month <= 1 else "bahorgi"


def upsert_dim_time(olap_db: Session, d: date) -> int:
    """dim_time ga yozuvni qo'shish (idempotent), key qaytarish."""
    existing = olap_db.query(DimTime).filter(DimTime.full_date == d).first()
    if existing:
        return existing.time_key

    dt = DimTime(
        full_date=d,
        day=d.day,
        week=d.isocalendar()[1],
        month=d.month,
        month_name=_get_month_name(d.month),
        quarter=(d.month - 1) // 3 + 1,
        semester=_semester_from_date(d),
        academic_year=_academic_year_from_date(d),
        year=d.year,
    )
    olap_db.add(dt)
    olap_db.flush()
    return dt.time_key


def upsert_dim_student(olap_db: Session, student: Student) -> int:
    existing = olap_db.query(DimStudent).filter(DimStudent.student_id == student.student_id).first()
    if existing:
        return existing.student_key

    group = student.group
    ds = DimStudent(
        student_id=student.student_id,
        full_name=student.full_name,
        gender=student.gender.value,
        birth_date=student.birth_date,
        enrollment_year=student.enrollment_year,
        group_name=group.name if group else "",
        education_form=student.education_form.value,
        status=student.status.value,
    )
    olap_db.add(ds)
    olap_db.flush()
    return ds.student_key


def upsert_dim_subject(olap_db: Session, subject: Subject) -> int:
    existing = olap_db.query(DimSubject).filter(DimSubject.subject_code == subject.code).first()
    if existing:
        return existing.subject_key

    ds = DimSubject(
        subject_code=subject.code,
        subject_name=subject.name,
        department=subject.department,
        credit_hours=subject.credit_hours,
        subject_type=subject.subject_type.value,
        semester=subject.semester,
    )
    olap_db.add(ds)
    olap_db.flush()
    return ds.subject_key


def upsert_dim_teacher(olap_db: Session, teacher: Teacher) -> int:
    existing = olap_db.query(DimTeacher).filter(DimTeacher.teacher_id == teacher.teacher_id).first()
    if existing:
        return existing.teacher_key

    dt = DimTeacher(
        teacher_id=teacher.teacher_id,
        full_name=teacher.full_name,
        academic_degree=teacher.academic_degree,
        position=teacher.position,
        department=teacher.department,
    )
    olap_db.add(dt)
    olap_db.flush()
    return dt.teacher_key


def upsert_dim_faculty(olap_db: Session, group: Group) -> int:
    """Faculty dimension uchun group asosida yozuv yaratish."""
    specialty = group.specialty
    faculty = specialty.faculty

    existing = (
        olap_db.query(DimFaculty)
        .filter(
            DimFaculty.faculty_name == faculty.name,
            DimFaculty.specialty == specialty.name,
            DimFaculty.course == group.course,
            DimFaculty.group_name == group.name,
        )
        .first()
    )
    if existing:
        return existing.faculty_key

    df = DimFaculty(
        faculty_name=faculty.name,
        department=faculty.description,
        specialty=specialty.name,
        course=group.course,
        group_name=group.name,
    )
    olap_db.add(df)
    olap_db.flush()
    return df.faculty_key


def upsert_dim_assessment(olap_db: Session, atype: AssessmentType) -> int:
    existing = olap_db.query(DimAssessmentType).filter(DimAssessmentType.type_name == atype.name).first()
    if existing:
        return existing.assessment_type_key

    da = DimAssessmentType(
        type_name=atype.name,
        weight_percentage=float(atype.weight_percentage),
        description=atype.description,
    )
    olap_db.add(da)
    olap_db.flush()
    return da.assessment_type_key


def _gpa_from_grade(grade_value: float) -> float:
    """100 ballik tizimdan 4.0 shkalaga o'tkazish."""
    if grade_value >= 90:
        return 4.0
    if grade_value >= 85:
        return 3.7
    if grade_value >= 80:
        return 3.3
    if grade_value >= 75:
        return 3.0
    if grade_value >= 70:
        return 2.7
    if grade_value >= 65:
        return 2.3
    if grade_value >= 60:
        return 2.0
    if grade_value >= 55:
        return 1.7
    return 0.0


def run_full_etl(batch_size: int = 1000) -> dict[str, Any]:
    """OLTP -> OLAP to'liq ETL.

    Idempotent: qayta ishga tushirilsa dimension lar duplicate bo'lmaydi.
    Fact jadval har safar yangidan to'ldiriladi (truncate + load).
    Performance: dimension keylarini cache lab fact loop da qayta query qilinmaydi.
    """
    started_at = datetime.utcnow()
    logger.info("ETL boshlandi: {}", started_at)

    stats = {"dim_loaded": 0, "fact_loaded": 0, "errors": 0}

    with oltp_session() as oltp_db, olap_session() as olap_db:
        # 1. Barcha dimension lar — bir martada
        for student in oltp_db.query(Student).all():
            upsert_dim_student(olap_db, student)
            stats["dim_loaded"] += 1
        for subject in oltp_db.query(Subject).all():
            upsert_dim_subject(olap_db, subject)
        for teacher in oltp_db.query(Teacher).all():
            upsert_dim_teacher(olap_db, teacher)
        for group in oltp_db.query(Group).all():
            upsert_dim_faculty(olap_db, group)
        for atype in oltp_db.query(AssessmentType).all():
            upsert_dim_assessment(olap_db, atype)
        olap_db.commit()

        # 2. Dimension keylarini in-memory cache ga olish — har fact yozuv uchun query qilmaslik
        student_cache: dict[int, int] = {
            oltp_id: olap_key
            for oltp_id, olap_key in olap_db.execute(
                text(
                    "SELECT s.id AS oltp_id, d.student_key FROM dim_student d "
                    "JOIN (SELECT id, student_id FROM students) s ON d.student_id = s.student_id"
                )
            ).fetchall()
        } if False else {
            s.id: olap_db.query(DimStudent.student_key).filter(DimStudent.student_id == s.student_id).scalar()
            for s in oltp_db.query(Student).all()
        }
        subject_cache: dict[int, int] = {
            s.id: olap_db.query(DimSubject.subject_key).filter(DimSubject.subject_code == s.code).scalar()
            for s in oltp_db.query(Subject).all()
        }
        teacher_cache: dict[int, int] = {
            t.id: olap_db.query(DimTeacher.teacher_key).filter(DimTeacher.teacher_id == t.teacher_id).scalar()
            for t in oltp_db.query(Teacher).all()
        }
        assessment_cache: dict[int, int] = {
            a.id: olap_db.query(DimAssessmentType.assessment_type_key).filter(DimAssessmentType.type_name == a.name).scalar()
            for a in oltp_db.query(AssessmentType).all()
        }
        faculty_cache: dict[int, int] = {}  # group_id -> faculty_key
        for group in oltp_db.query(Group).all():
            specialty = group.specialty
            faculty = specialty.faculty
            key = (
                olap_db.query(DimFaculty.faculty_key)
                .filter(
                    DimFaculty.faculty_name == faculty.name,
                    DimFaculty.specialty == specialty.name,
                    DimFaculty.course == group.course,
                    DimFaculty.group_name == group.name,
                )
                .scalar()
            )
            faculty_cache[group.id] = key

        credit_cache: dict[int, int] = {s.id: s.credit_hours for s in oltp_db.query(Subject).all()}

        # 3. Fact: avval tozalash
        try:
            olap_db.execute(text("TRUNCATE TABLE fact_student_grades RESTART IDENTITY"))
        except Exception:
            olap_db.execute(text("DELETE FROM fact_student_grades"))
        olap_db.commit()

        # 4. Fact loop — endi cache lardan tezda foydalanamiz
        time_cache: dict[date, int] = {}
        batch: list[FactStudentGrade] = []
        total = oltp_db.query(Grade).count()
        logger.info("Jami {} ta baho qayta ishlanadi", total)

        for grade in oltp_db.query(Grade).yield_per(batch_size):
            try:
                if grade.grade_date not in time_cache:
                    time_cache[grade.grade_date] = upsert_dim_time(olap_db, grade.grade_date)
                    olap_db.commit()
                time_key = time_cache[grade.grade_date]

                # Faculty key talaba guruhi orqali
                faculty_key = faculty_cache.get(grade.student.group_id)

                fact = FactStudentGrade(
                    student_key=student_cache[grade.student_id],
                    subject_key=subject_cache[grade.subject_id],
                    teacher_key=teacher_cache[grade.teacher_id],
                    time_key=time_key,
                    faculty_key=faculty_key,
                    assessment_type_key=assessment_cache[grade.assessment_type_id],
                    grade_value=float(grade.grade_value),
                    credit_hours=credit_cache.get(grade.subject_id, 3),
                    attendance_percentage=float(grade.attendance_percentage),
                    gpa_points=_gpa_from_grade(float(grade.grade_value)),
                    is_passed=grade.is_passed,
                )
                batch.append(fact)

                if len(batch) >= batch_size:
                    olap_db.bulk_save_objects(batch)
                    olap_db.commit()
                    stats["fact_loaded"] += len(batch)
                    logger.info("Yuklangan: {} / {}", stats["fact_loaded"], total)
                    batch = []
            except Exception as e:
                logger.error("ETL xatosi: {}", e)
                stats["errors"] += 1

        if batch:
            olap_db.bulk_save_objects(batch)
            olap_db.commit()
            stats["fact_loaded"] += len(batch)

    finished_at = datetime.utcnow()
    duration = (finished_at - started_at).total_seconds()
    stats["duration_sec"] = duration
    stats["started_at"] = started_at.isoformat()
    stats["finished_at"] = finished_at.isoformat()
    logger.info("ETL tugadi: {} sek, stats: {}", duration, stats)
    return stats


def refresh_materialized_views() -> None:
    """OLAP da materialized view larni yangilash (agar mavjud bo'lsa)."""
    with olap_session() as db:
        try:
            db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_faculty_semester_avg"))
        except Exception as e:
            logger.warning("MV refresh skip: {}", e)
