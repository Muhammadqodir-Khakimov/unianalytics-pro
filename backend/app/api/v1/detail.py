"""Detail (profil) sahifalari uchun batafsil ma'lumot endpointlari.

Har bir resurs uchun: asosiy ma'lumot + statistika + tarix + grafiklar.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import require_any
from app.database import get_olap_db, get_oltp_db
from app.models.oltp.faculty import Faculty
from app.models.oltp.grade import Grade
from app.models.oltp.student import Student
from app.models.oltp.subject import Subject
from app.models.oltp.teacher import Teacher

router = APIRouter(prefix="/detail", tags=["Detail sahifalar"], dependencies=[Depends(require_any)])


@router.get("/student/{student_id}")
def student_detail(
    student_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    """Talaba batafsil profili."""
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Talaba topilmadi")

    sid = student.student_id

    stats = olap.execute(
        text(
            """
            SELECT COUNT(*) AS grades_count,
                   ROUND(AVG(grade_value), 2) AS avg_grade,
                   ROUND(AVG(gpa_points), 3) AS avg_gpa,
                   ROUND(AVG(attendance_percentage), 2) AS avg_attendance,
                   COUNT(DISTINCT subject_key) AS subjects_count,
                   MAX(grade_value) AS max_grade,
                   MIN(grade_value) AS min_grade,
                   SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) AS passed,
                   SUM(CASE WHEN is_passed THEN 0 ELSE 1 END) AS failed
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.student_id = :sid
            """
        ),
        {"sid": sid},
    ).mappings().first() or {}

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
        {"sid": sid},
    ).mappings().all()

    by_subject = olap.execute(
        text(
            """
            SELECT s.subject_name, s.department, s.credit_hours,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   ROUND(AVG(f.gpa_points), 3) AS avg_gpa,
                   COUNT(*) AS grades_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE ds.student_id = :sid
            GROUP BY s.subject_name, s.department, s.credit_hours
            ORDER BY avg_grade DESC
            """
        ),
        {"sid": sid},
    ).mappings().all()

    # Group ichida o'rin
    rank = olap.execute(
        text(
            """
            WITH g AS (
                SELECT ds.student_id, AVG(f.gpa_points) AS gpa,
                       RANK() OVER (ORDER BY AVG(f.gpa_points) DESC) AS rnk
                FROM fact_student_grades f
                JOIN dim_student ds ON f.student_key = ds.student_key
                WHERE ds.group_name = :grp
                GROUP BY ds.student_id
            )
            SELECT rnk, (SELECT COUNT(*) FROM g) AS total
            FROM g WHERE student_id = :sid
            """
        ),
        {"sid": sid, "grp": student.group.name if student.group else ""},
    ).mappings().first() or {}

    return {
        "student": {
            "id": student.id,
            "student_id": student.student_id,
            "full_name": student.full_name,
            "gender": student.gender.value,
            "birth_date": student.birth_date.isoformat() if student.birth_date else None,
            "phone": student.phone,
            "email": student.email,
            "education_form": student.education_form.value,
            "status": student.status.value,
            "enrollment_year": student.enrollment_year,
            "group_name": student.group.name if student.group else None,
            "course": student.group.course if student.group else None,
            "specialty": student.group.specialty.name if student.group and student.group.specialty else None,
            "faculty": student.group.specialty.faculty.name if student.group and student.group.specialty else None,
        },
        "stats": dict(stats),
        "rank": dict(rank),
        "gpa_trend": [dict(r) for r in trend],
        "by_subject": [dict(r) for r in by_subject],
    }


@router.get("/teacher/{teacher_id}")
def teacher_detail(
    teacher_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    teacher = oltp.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(404, "O'qituvchi topilmadi")

    tid = teacher.teacher_id

    stats = olap.execute(
        text(
            """
            SELECT COUNT(*) AS grades_given,
                   COUNT(DISTINCT student_key) AS students_taught,
                   COUNT(DISTINCT subject_key) AS subjects_taught,
                   ROUND(AVG(grade_value), 2) AS avg_grade_given,
                   ROUND(AVG(gpa_points), 3) AS avg_gpa
            FROM fact_student_grades f
            JOIN dim_teacher dt ON f.teacher_key = dt.teacher_key
            WHERE dt.teacher_id = :tid
            """
        ),
        {"tid": tid},
    ).mappings().first() or {}

    subjects = olap.execute(
        text(
            """
            SELECT s.subject_name, s.department,
                   COUNT(DISTINCT f.student_key) AS students,
                   COUNT(*) AS grades_count,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade
            FROM fact_student_grades f
            JOIN dim_teacher dt ON f.teacher_key = dt.teacher_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE dt.teacher_id = :tid
            GROUP BY s.subject_name, s.department
            ORDER BY students DESC
            """
        ),
        {"tid": tid},
    ).mappings().all()

    trend = olap.execute(
        text(
            """
            SELECT t.academic_year, t.semester,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   COUNT(*) AS grades
            FROM fact_student_grades f
            JOIN dim_teacher dt ON f.teacher_key = dt.teacher_key
            JOIN dim_time t ON f.time_key = t.time_key
            WHERE dt.teacher_id = :tid
            GROUP BY t.academic_year, t.semester
            ORDER BY t.academic_year, t.semester
            """
        ),
        {"tid": tid},
    ).mappings().all()

    return {
        "teacher": {
            "id": teacher.id,
            "teacher_id": teacher.teacher_id,
            "full_name": teacher.full_name,
            "academic_degree": teacher.academic_degree,
            "position": teacher.position,
            "department": teacher.department,
            "phone": teacher.phone,
            "email": teacher.email,
        },
        "stats": dict(stats),
        "subjects": [dict(r) for r in subjects],
        "trend": [dict(r) for r in trend],
    }


@router.get("/subject/{subject_id}")
def subject_detail(
    subject_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    subject = oltp.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(404, "Fan topilmadi")

    code = subject.code

    stats = olap.execute(
        text(
            """
            SELECT COUNT(*) AS grades_count,
                   COUNT(DISTINCT student_key) AS students_count,
                   COUNT(DISTINCT teacher_key) AS teachers_count,
                   ROUND(AVG(grade_value), 2) AS avg_grade,
                   ROUND(AVG(gpa_points), 3) AS avg_gpa,
                   MAX(grade_value) AS max_grade,
                   MIN(grade_value) AS min_grade,
                   ROUND(SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS passing_rate
            FROM fact_student_grades f
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE s.subject_code = :code
            """
        ),
        {"code": code},
    ).mappings().first() or {}

    # Top 10 talaba bu fan bo'yicha
    top = olap.execute(
        text(
            """
            SELECT ds.student_id, ds.full_name, ds.group_name,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE s.subject_code = :code
            GROUP BY ds.student_id, ds.full_name, ds.group_name
            ORDER BY avg_grade DESC
            LIMIT 10
            """
        ),
        {"code": code},
    ).mappings().all()

    # Ball taqsimoti (histogram bucket)
    distribution = olap.execute(
        text(
            """
            SELECT
                SUM(CASE WHEN grade_value < 55 THEN 1 ELSE 0 END) AS bucket_fail,
                SUM(CASE WHEN grade_value >= 55 AND grade_value < 70 THEN 1 ELSE 0 END) AS bucket_d,
                SUM(CASE WHEN grade_value >= 70 AND grade_value < 85 THEN 1 ELSE 0 END) AS bucket_c,
                SUM(CASE WHEN grade_value >= 85 AND grade_value < 90 THEN 1 ELSE 0 END) AS bucket_b,
                SUM(CASE WHEN grade_value >= 90 THEN 1 ELSE 0 END) AS bucket_a
            FROM fact_student_grades f
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE s.subject_code = :code
            """
        ),
        {"code": code},
    ).mappings().first() or {}

    return {
        "subject": {
            "id": subject.id,
            "code": subject.code,
            "name": subject.name,
            "department": subject.department,
            "credit_hours": subject.credit_hours,
            "subject_type": subject.subject_type.value,
            "semester": subject.semester,
            "description": subject.description,
        },
        "stats": dict(stats),
        "top_students": [dict(r) for r in top],
        "distribution": dict(distribution),
    }


@router.get("/faculty/{faculty_id}")
def faculty_detail(
    faculty_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    faculty = oltp.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(404, "Fakultet topilmadi")

    fname = faculty.name

    stats = olap.execute(
        text(
            """
            SELECT COUNT(*) AS grades_count,
                   COUNT(DISTINCT student_key) AS students_count,
                   COUNT(DISTINCT teacher_key) AS teachers_count,
                   COUNT(DISTINCT subject_key) AS subjects_count,
                   ROUND(AVG(grade_value), 2) AS avg_grade,
                   ROUND(AVG(gpa_points), 3) AS avg_gpa,
                   ROUND(SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS passing_rate
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            WHERE fac.faculty_name = :fname
            """
        ),
        {"fname": fname},
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
        {"fname": fname},
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
        {"fname": fname},
    ).mappings().all()

    trend = olap.execute(
        text(
            """
            SELECT t.academic_year, t.semester,
                   ROUND(AVG(f.gpa_points), 3) AS avg_gpa,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            JOIN dim_time t ON f.time_key = t.time_key
            WHERE fac.faculty_name = :fname
            GROUP BY t.academic_year, t.semester
            ORDER BY t.academic_year, t.semester
            """
        ),
        {"fname": fname},
    ).mappings().all()

    return {
        "faculty": {
            "id": faculty.id,
            "name": faculty.name,
            "code": faculty.code,
            "description": faculty.description,
        },
        "stats": dict(stats),
        "by_specialty": [dict(r) for r in by_specialty],
        "by_course": [dict(r) for r in by_course],
        "trend": [dict(r) for r in trend],
    }
