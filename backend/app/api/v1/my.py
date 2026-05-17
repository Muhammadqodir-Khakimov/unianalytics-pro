"""Rolga bog'liq "mening ma'lumotlarim" endpointlari.

Talaba: o'z baholari, GPA dinamikasi
O'qituvchi: o'z guruhlari, fanlari, kiritgan baholari
Dekan: o'z fakulteti statistikasi
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_olap_db, get_oltp_db
from app.models.oltp.faculty import Faculty
from app.models.oltp.grade import Grade
from app.models.oltp.student import Student
from app.models.oltp.subject import Subject
from app.models.oltp.teacher import Teacher
from app.models.oltp.user import User, UserRole

router = APIRouter(prefix="/my", tags=["Mening hisobim"])


@router.get("/grades")
def my_grades(
    page: int = 1,
    page_size: int = 10,
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> dict[str, Any]:
    """Joriy talabaning baholari (bot/mobile uchun)."""
    page = max(1, int(page or 1))
    page_size = max(1, min(int(page_size or 10), 100))

    student = _link_student(user, oltp)
    if not student:
        return {"items": [], "total": 0, "total_pages": 0, "page": page,
                "page_size": page_size, "message": "Talaba hisobiga bog'lanmagan"}

    q = (
        oltp.query(Grade, Subject)
        .outerjoin(Subject, Subject.id == Grade.subject_id)
        .filter(Grade.student_id == student.id)
        .order_by(Grade.grade_date.desc())
    )
    total = q.count()
    rows = q.offset((page - 1) * page_size).limit(page_size).all()

    type_names = {1: "JN", 2: "ON", 3: "YN", 4: "Yakuniy"}
    items = [
        {
            "id": g.id,
            "subject_id": g.subject_id,
            "subject_name": s.name if s else f"Fan #{g.subject_id}",
            "assessment_type": type_names.get(g.assessment_type_id, ""),
            "grade_value": float(g.grade_value),
            "attendance_percentage": float(g.attendance_percentage) if g.attendance_percentage else None,
            "is_passed": g.is_passed,
            "semester": g.semester,
            "academic_year": g.academic_year,
            "grade_date": g.grade_date.isoformat() if g.grade_date else None,
        }
        for g, s in rows
    ]
    return {
        "items": items,
        "total": total,
        "total_pages": max(1, -(-total // page_size)),
        "page": page,
        "page_size": page_size,
    }


@router.get("/dashboard")
def my_dashboard(
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
) -> dict[str, Any]:
    """Rolga qarab kerakli dashboard ma'lumotlarini qaytaradi."""
    if user.role == UserRole.STUDENT:
        return _student_dashboard(user, oltp, olap)
    if user.role == UserRole.TEACHER:
        return _teacher_dashboard(user, oltp, olap)
    if user.role == UserRole.DEKAN:
        return _dean_dashboard(user, oltp, olap)
    return _admin_dashboard(olap)


def _link_student(user: User, oltp: Session) -> Student | None:
    """User ni Student bilan bog'lash — username asosida (yoki email)."""
    if user.role != UserRole.STUDENT:
        return None
    # Username "student" — demo akkaunt. Birinchi baholar bo'lgan talabani
    # qaytaramiz (Aks holda dashboard bo'sh ko'rinadi, chunki seed har bir
    # talabaga emas, tasodifiy tanlanganlariga baho beradi).
    if user.username == "student":
        s = (
            oltp.query(Student)
            .join(Grade, Grade.student_id == Student.id)
            .group_by(Student.id)
            .order_by(Student.id)
            .first()
        )
        return s or oltp.query(Student).first()
    # Aks holda email yoki user_id orqali
    return (
        oltp.query(Student)
        .filter((Student.email == user.email) | (Student.user_id == user.id))
        .first()
    )


def _link_teacher(user: User, oltp: Session) -> Teacher | None:
    if user.role != UserRole.TEACHER:
        return None
    if user.username == "teacher":
        return oltp.query(Teacher).first()
    return (
        oltp.query(Teacher)
        .filter((Teacher.email == user.email) | (Teacher.user_id == user.id))
        .first()
    )


def _student_dashboard(user: User, oltp: Session, olap: Session) -> dict:
    student = _link_student(user, oltp)
    if not student:
        return {"role": "student", "linked": False, "message": "Talaba hisobi bog'lanmagan"}

    # Talaba GPA va statistika
    stats = olap.execute(
        text(
            """
            SELECT
                COUNT(*) AS grades_count,
                ROUND(AVG(grade_value), 2) AS avg_grade,
                ROUND(AVG(gpa_points), 3) AS avg_gpa,
                ROUND(AVG(attendance_percentage), 2) AS avg_attendance,
                COUNT(DISTINCT subject_key) AS subjects_count,
                SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) AS passed_count,
                SUM(CASE WHEN is_passed THEN 0 ELSE 1 END) AS failed_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.student_id = :sid
            """
        ),
        {"sid": student.student_id},
    ).mappings().first() or {}

    # GPA dinamika
    trend = olap.execute(
        text(
            """
            SELECT t.academic_year, t.semester,
                   ROUND(AVG(f.gpa_points), 3) AS gpa,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   COUNT(*) AS grades
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_time t ON f.time_key = t.time_key
            WHERE ds.student_id = :sid
            GROUP BY t.academic_year, t.semester
            ORDER BY t.academic_year, t.semester
            """
        ),
        {"sid": student.student_id},
    ).mappings().all()

    # Fan kesimida
    by_subject = olap.execute(
        text(
            """
            SELECT s.subject_name, s.department,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   COUNT(*) AS grades_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE ds.student_id = :sid
            GROUP BY s.subject_name, s.department
            ORDER BY avg_grade DESC
            """
        ),
        {"sid": student.student_id},
    ).mappings().all()

    # Akademik o'rin (rank): GPA bo'yicha guruh ichida nechinchi
    rank = olap.execute(
        text(
            """
            WITH gpa_rank AS (
                SELECT ds.student_id, AVG(f.gpa_points) AS gpa,
                       RANK() OVER (ORDER BY AVG(f.gpa_points) DESC) AS rnk
                FROM fact_student_grades f
                JOIN dim_student ds ON f.student_key = ds.student_key
                WHERE ds.group_name = :grp
                GROUP BY ds.student_id
            )
            SELECT rnk, (SELECT COUNT(*) FROM gpa_rank) AS total
            FROM gpa_rank WHERE student_id = :sid
            """
        ),
        {"sid": student.student_id, "grp": student.group.name if student.group else ""},
    ).mappings().first() or {"rnk": None, "total": None}

    return {
        "role": "student",
        "linked": True,
        "student": {
            "student_id": student.student_id,
            "full_name": student.full_name,
            "group_name": student.group.name if student.group else None,
            "course": student.group.course if student.group else None,
            "enrollment_year": student.enrollment_year,
            "status": student.status.value,
        },
        "stats": dict(stats),
        "rank": dict(rank),
        "gpa_trend": [dict(r) for r in trend],
        "by_subject": [dict(r) for r in by_subject],
    }


def _teacher_dashboard(user: User, oltp: Session, olap: Session) -> dict:
    teacher = _link_teacher(user, oltp)
    if not teacher:
        return {"role": "teacher", "linked": False, "message": "O'qituvchi hisobi bog'lanmagan"}

    stats = olap.execute(
        text(
            """
            SELECT COUNT(*) AS grades_given,
                   COUNT(DISTINCT student_key) AS students_taught,
                   COUNT(DISTINCT subject_key) AS subjects_taught,
                   ROUND(AVG(grade_value), 2) AS avg_grade,
                   ROUND(AVG(gpa_points), 3) AS avg_gpa
            FROM fact_student_grades f
            JOIN dim_teacher dt ON f.teacher_key = dt.teacher_key
            WHERE dt.teacher_id = :tid
            """
        ),
        {"tid": teacher.teacher_id},
    ).mappings().first() or {}

    by_subject = olap.execute(
        text(
            """
            SELECT s.subject_name,
                   COUNT(*) AS grades_count,
                   COUNT(DISTINCT f.student_key) AS students_count,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   ROUND(AVG(f.gpa_points), 3) AS avg_gpa
            FROM fact_student_grades f
            JOIN dim_teacher dt ON f.teacher_key = dt.teacher_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE dt.teacher_id = :tid
            GROUP BY s.subject_name
            ORDER BY grades_count DESC
            """
        ),
        {"tid": teacher.teacher_id},
    ).mappings().all()

    recent_grades = (
        oltp.query(Grade)
        .filter(Grade.teacher_id == teacher.id)
        .order_by(Grade.grade_date.desc())
        .limit(20)
        .all()
    )

    return {
        "role": "teacher",
        "linked": True,
        "teacher": {
            "teacher_id": teacher.teacher_id,
            "full_name": teacher.full_name,
            "department": teacher.department,
            "position": teacher.position,
        },
        "stats": dict(stats),
        "by_subject": [dict(r) for r in by_subject],
        "recent_grades": [
            {
                "id": g.id,
                "student_id": g.student_id,
                "subject_id": g.subject_id,
                "grade_value": float(g.grade_value),
                "academic_year": g.academic_year,
                "semester": g.semester,
                "grade_date": g.grade_date.isoformat(),
            }
            for g in recent_grades
        ],
    }


def _dean_dashboard(user: User, oltp: Session, olap: Session) -> dict:
    """Dekan: birinchi fakultet (real tizimda user_id orqali bog'lash)."""
    faculty = oltp.query(Faculty).first()
    if not faculty:
        return {"role": "dean", "linked": False}

    stats = olap.execute(
        text(
            """
            SELECT COUNT(*) AS total_grades,
                   COUNT(DISTINCT f.student_key) AS total_students,
                   COUNT(DISTINCT f.teacher_key) AS total_teachers,
                   COUNT(DISTINCT f.subject_key) AS total_subjects,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   ROUND(AVG(f.gpa_points), 3) AS avg_gpa,
                   ROUND(AVG(f.attendance_percentage), 2) AS avg_attendance,
                   ROUND(SUM(CASE WHEN f.is_passed THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS passing_rate
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            WHERE fac.faculty_name = :fname
            """
        ),
        {"fname": faculty.name},
    ).mappings().first() or {}

    by_specialty = olap.execute(
        text(
            """
            SELECT fac.specialty,
                   COUNT(DISTINCT f.student_key) AS students,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   ROUND(AVG(f.gpa_points), 3) AS avg_gpa
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            WHERE fac.faculty_name = :fname
            GROUP BY fac.specialty
            ORDER BY avg_gpa DESC
            """
        ),
        {"fname": faculty.name},
    ).mappings().all()

    by_course = olap.execute(
        text(
            """
            SELECT fac.course,
                   COUNT(DISTINCT f.student_key) AS students,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   ROUND(AVG(f.gpa_points), 3) AS avg_gpa
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            WHERE fac.faculty_name = :fname
            GROUP BY fac.course
            ORDER BY fac.course
            """
        ),
        {"fname": faculty.name},
    ).mappings().all()

    return {
        "role": "dean",
        "linked": True,
        "faculty": {"id": faculty.id, "name": faculty.name, "code": faculty.code},
        "stats": dict(stats),
        "by_specialty": [dict(r) for r in by_specialty],
        "by_course": [dict(r) for r in by_course],
    }


def _admin_dashboard(olap: Session) -> dict:
    stats = olap.execute(
        text(
            """
            SELECT COUNT(*) AS total_grades,
                   COUNT(DISTINCT student_key) AS total_students,
                   COUNT(DISTINCT subject_key) AS total_subjects,
                   COUNT(DISTINCT teacher_key) AS total_teachers,
                   ROUND(AVG(grade_value), 2) AS avg_grade,
                   ROUND(AVG(gpa_points), 3) AS avg_gpa
            FROM fact_student_grades
            """
        )
    ).mappings().first() or {}
    return {"role": "admin", "linked": True, "stats": dict(stats)}
