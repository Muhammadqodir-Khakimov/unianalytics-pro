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


@router.get("/grade-distribution")
def grade_distribution(db: Session = Depends(get_olap_db)):
    """Baholar histogrami (bell curve uchun) — barcha individual baholar."""
    sql = text("SELECT grade_value FROM fact_student_grades WHERE grade_value IS NOT NULL")
    rows = db.execute(sql).fetchall()
    return [float(r[0]) for r in rows]


@router.get("/faculty-radar")
def faculty_radar(db: Session = Depends(get_olap_db)):
    """Fakultetlar uchun radar chart — 5 o'lcham:
    GPA, Davomat, Faollik (baho intensivligi), O'tish foizi, Talabalar o'sishi."""
    sql = text(
        """
        SELECT fac.faculty_name AS name,
               ROUND(AVG(f.gpa_points)::numeric * 1.25, 2)              AS gpa,
               ROUND(AVG(f.attendance_percentage)::numeric / 20.0, 2)   AS attendance,
               ROUND(LEAST(COUNT(*)::numeric / 200.0, 5), 2)            AS activity,
               ROUND(SUM(CASE WHEN f.is_passed THEN 1 ELSE 0 END) * 5.0
                     / NULLIF(COUNT(*), 0), 2)                          AS pass_rate,
               ROUND(LEAST(COUNT(DISTINCT f.student_key)::numeric / 50.0, 5), 2) AS growth
        FROM fact_student_grades f
        JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
        GROUP BY fac.faculty_name
        ORDER BY gpa DESC
        LIMIT 6
        """
    )
    rows = db.execute(sql).mappings().all()
    return {
        "axes": ["GPA", "Davomat", "Faollik", "O'tish", "Talabalar"],
        "series": [
            {
                "name": r["name"],
                "values": [
                    float(r["gpa"] or 0),
                    float(r["attendance"] or 0),
                    float(r["activity"] or 0),
                    float(r["pass_rate"] or 0),
                    float(r["growth"] or 0),
                ],
            }
            for r in rows
        ],
    }


@router.get("/attendance-heatmap")
def attendance_heatmap(db: Session = Depends(get_olap_db)):
    """Kun × soat heatmap — schedule entries soni va davomat o'rtachasi."""
    # Schedule jadval kun (0-6) × start_hour bo'yicha — agar bo'sh bo'lsa demo
    from sqlalchemy import text as sql_text
    try:
        rows = db.execute(
            sql_text(
                """
                SELECT EXTRACT(DOW FROM s.full_date)::int AS dow,
                       EXTRACT(HOUR FROM f.created_at)::int AS hour,
                       COUNT(*) AS cnt,
                       ROUND(AVG(f.attendance_percentage)::numeric, 1) AS att
                FROM fact_student_grades f
                JOIN dim_time s ON f.time_key = s.time_key
                WHERE f.created_at IS NOT NULL
                GROUP BY dow, hour
                """
            )
        ).mappings().all()
    except Exception:
        rows = []

    days = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]
    result = []
    if rows:
        for r in rows:
            d = int(r["dow"]) if r["dow"] is not None else 0
            h = int(r["hour"]) if r["hour"] is not None else 8
            if 0 <= d < 7 and 8 <= h <= 18:
                result.append({"row": days[d], "col": f"{h}:00", "value": int(r["cnt"])})
    # Bo'sh joylarni 0 bilan to'ldirish (heatmap to'liq panjara)
    seen = {(r["row"], r["col"]) for r in result}
    for d in days:
        for h in range(8, 18):
            if (d, f"{h}:00") not in seen:
                result.append({"row": d, "col": f"{h}:00", "value": 0})
    return result
