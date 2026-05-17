"""Dashboard endpointlari — tayyor agregatsiya, widget uchun."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import require_any
from app.database import get_olap_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(require_any)])


@router.get("/summary")
def summary(db: Session = Depends(get_olap_db)):
    """Asosiy ko'rsatkichlar: jami baholar, talabalar, o'rtacha GPA va h.k."""
    sql = text(
        """
        SELECT
            COUNT(*) AS total_grades,
            COUNT(DISTINCT student_key) AS total_students,
            COUNT(DISTINCT subject_key) AS total_subjects,
            COUNT(DISTINCT teacher_key) AS total_teachers,
            ROUND(AVG(grade_value), 2) AS avg_grade,
            ROUND(AVG(gpa_points), 2) AS avg_gpa,
            ROUND(AVG(attendance_percentage), 2) AS avg_attendance,
            ROUND((SUM(CASE WHEN is_passed THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS passing_rate
        FROM fact_student_grades
        """
    )
    row = db.execute(sql).mappings().first()
    return dict(row) if row else {}


@router.get("/gpa-trend")
def gpa_trend(db: Session = Depends(get_olap_db)):
    """GPA dinamikasi vaqt bo'yicha (academic_year + semester)."""
    sql = text(
        """
        SELECT t.academic_year, t.semester,
               ROUND(AVG(f.gpa_points), 3) AS avg_gpa,
               ROUND(AVG(f.grade_value), 2) AS avg_grade,
               COUNT(*) AS grades_count
        FROM fact_student_grades f
        JOIN dim_time t ON f.time_key = t.time_key
        GROUP BY t.academic_year, t.semester
        ORDER BY t.academic_year, t.semester
        """
    )
    rows = db.execute(sql).mappings().all()
    return [dict(r) for r in rows]


@router.get("/faculty-comparison")
def faculty_comparison(db: Session = Depends(get_olap_db)):
    """Fakultetlar bo'yicha o'rtacha ko'rsatkichlar."""
    sql = text(
        """
        SELECT fac.faculty_name,
               ROUND(AVG(f.grade_value), 2) AS avg_grade,
               ROUND(AVG(f.gpa_points), 2) AS avg_gpa,
               COUNT(DISTINCT f.student_key) AS students_count,
               COUNT(*) AS grades_count
        FROM fact_student_grades f
        JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
        GROUP BY fac.faculty_name
        ORDER BY avg_gpa DESC
        """
    )
    rows = db.execute(sql).mappings().all()
    return [dict(r) for r in rows]


@router.get("/top-students")
def top_students(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_olap_db)):
    """TOP-N talabalar GPA bo'yicha."""
    sql = text(
        """
        SELECT s.student_id, s.full_name, s.group_name,
               ROUND(AVG(f.gpa_points), 3) AS avg_gpa,
               ROUND(AVG(f.grade_value), 2) AS avg_grade,
               COUNT(*) AS grades_count
        FROM fact_student_grades f
        JOIN dim_student s ON f.student_key = s.student_key
        GROUP BY s.student_id, s.full_name, s.group_name
        HAVING COUNT(*) >= 5
        ORDER BY avg_gpa DESC
        LIMIT :limit
        """
    )
    rows = db.execute(sql, {"limit": limit}).mappings().all()
    return [dict(r) for r in rows]


@router.get("/subject-performance")
def subject_performance(db: Session = Depends(get_olap_db)):
    """Fanlar bo'yicha o'zlashtirish."""
    sql = text(
        """
        SELECT sub.subject_name, sub.department,
               ROUND(AVG(f.grade_value), 2) AS avg_grade,
               ROUND(AVG(f.gpa_points), 2) AS avg_gpa,
               COUNT(*) AS grades_count,
               ROUND((SUM(CASE WHEN f.is_passed THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2) AS passing_rate
        FROM fact_student_grades f
        JOIN dim_subject sub ON f.subject_key = sub.subject_key
        GROUP BY sub.subject_name, sub.department
        ORDER BY avg_grade DESC
        """
    )
    rows = db.execute(sql).mappings().all()
    return [dict(r) for r in rows]


@router.get("/gender-distribution")
def gender_distribution(db: Session = Depends(get_olap_db)):
    """Gender bo'yicha o'zlashtirish."""
    sql = text(
        """
        SELECT s.gender,
               COUNT(DISTINCT s.student_key) AS students_count,
               ROUND(AVG(f.grade_value), 2) AS avg_grade,
               ROUND(AVG(f.gpa_points), 2) AS avg_gpa
        FROM fact_student_grades f
        JOIN dim_student s ON f.student_key = s.student_key
        GROUP BY s.gender
        """
    )
    rows = db.execute(sql).mappings().all()
    return [dict(r) for r in rows]


@router.get("/heatmap-faculty-semester")
def heatmap_faculty_semester(db: Session = Depends(get_olap_db)):
    """Fakultet x semestr heatmap uchun."""
    sql = text(
        """
        SELECT fac.faculty_name,
               t.academic_year || ' ' || t.semester AS period,
               ROUND(AVG(f.grade_value), 2) AS avg_grade
        FROM fact_student_grades f
        JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
        JOIN dim_time t ON f.time_key = t.time_key
        GROUP BY fac.faculty_name, t.academic_year, t.semester
        ORDER BY fac.faculty_name, t.academic_year, t.semester
        """
    )
    rows = db.execute(sql).mappings().all()
    return [dict(r) for r in rows]
