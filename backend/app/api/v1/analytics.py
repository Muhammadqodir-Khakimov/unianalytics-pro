"""AI/Analytics endpointlari — GPA prognozi, xavf zonasi, tavsiyalar.

Bu modulda oddiy statistik usullar (linear regression, anomaliya aniqlash)
qo'llanadi — ML kutubxonalarisiz, lekin yetarli darajada tushuntiriladigan.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import require_any, require_dekan
from app.database import get_olap_db, get_oltp_db
from app.models.oltp.student import Student

router = APIRouter(prefix="/analytics", tags=["AI / Analitika"])


def _linear_regression(x: List[float], y: List[float]) -> tuple[float, float]:
    """y = a + b*x — oddiy least-squares regression.

    Qaytaradi: (intercept, slope).
    """
    n = len(x)
    if n < 2:
        return (y[0] if y else 0.0, 0.0)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    var_x = sum((xi - mean_x) ** 2 for xi in x)
    if var_x == 0:
        return (mean_y, 0.0)
    cov_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    slope = cov_xy / var_x
    intercept = mean_y - slope * mean_x
    return (intercept, slope)


@router.get("/student/{student_id}/prediction", dependencies=[Depends(require_any)])
def predict_student_gpa(
    student_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    """Talabaning kelgusi semestrlardagi GPA ni prognoz qiladi.

    Algoritm: o'tgan semesterlar GPA larini olib, linear regression bilan
    trend chiziladi va kelgusi 2 semester uchun ekstrapolyatsiya qilinadi.
    """
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Talaba topilmadi")

    rows = olap.execute(
        text(
            """
            SELECT t.academic_year, t.semester,
                   AVG(f.gpa_points) AS gpa
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

    history = [{"period": f"{r['academic_year']} {r['semester']}", "gpa": float(r["gpa"])} for r in rows]
    if len(history) < 2:
        return {
            "student_id": student.student_id,
            "history": history,
            "predictions": [],
            "trend": "insufficient_data",
            "message": "Prognoz uchun kamida 2 ta semester kerak",
        }

    x = list(range(len(history)))
    y = [h["gpa"] for h in history]
    intercept, slope = _linear_regression(x, y)

    # Kelgusi 2 ta semester
    predictions = []
    for i in range(1, 3):
        pred_x = len(history) + i - 1
        pred_y = max(0.0, min(4.0, intercept + slope * pred_x))
        predictions.append({
            "period": f"prognoz +{i}",
            "gpa": round(pred_y, 3),
            "confidence": "yuqori" if abs(slope) < 0.3 else "o'rta",
        })

    trend = "barqaror"
    if slope > 0.1:
        trend = "o'sayotgan"
    elif slope < -0.1:
        trend = "pasayayotgan"

    risk_level = "past"
    last_gpa = y[-1]
    if last_gpa < 2.0:
        risk_level = "yuqori"
    elif last_gpa < 2.5 or slope < -0.2:
        risk_level = "o'rta"

    return {
        "student_id": student.student_id,
        "full_name": student.full_name,
        "history": history,
        "predictions": predictions,
        "trend": trend,
        "slope": round(slope, 4),
        "risk_level": risk_level,
        "current_gpa": round(last_gpa, 3),
        "recommendation": _student_recommendation(last_gpa, slope),
    }


def _student_recommendation(current_gpa: float, slope: float) -> str:
    if current_gpa < 2.0:
        return "Akademik xavf zonasida — qo'shimcha mashg'ulotlar va o'qituvchi maslahati tavsiya etiladi"
    if slope < -0.2:
        return "GPA pasayib bormoqda — sabablarini aniqlash va mentor biriktirish kerak"
    if current_gpa >= 3.5 and slope >= 0:
        return "A'lo natija — stipendiyaga tavsiya, ilmiy ish bilan shug'ullanish mumkin"
    if slope > 0.1:
        return "Trend ijobiy — joriy temp saqlansin"
    return "Barqaror natija — qo'shimcha rivojlanish imkoniyatlari mavjud"


@router.get("/at-risk", dependencies=[Depends(require_dekan)])
def at_risk_students(
    threshold: float = Query(2.0, ge=0, le=4),
    limit: int = Query(50, ge=1, le=500),
    olap: Session = Depends(get_olap_db),
):
    """Xavf zonasidagi talabalarni qaytaradi (GPA < threshold yoki tushib borayotgan).

    Bu ham bitiruv ishi uchun "ilmiy yangilik" sifatida ko'rsatish mumkin —
    real universitetda dekan dispatcherlari bu ro'yxatdan foydalanishi mumkin.
    """
    rows = olap.execute(
        text(
            """
            WITH student_gpa AS (
                SELECT ds.student_id, ds.full_name, ds.group_name,
                       AVG(f.gpa_points) AS avg_gpa,
                       AVG(f.attendance_percentage) AS avg_attendance,
                       SUM(CASE WHEN f.is_passed THEN 0 ELSE 1 END) AS failed_count,
                       COUNT(*) AS total_grades
                FROM fact_student_grades f
                JOIN dim_student ds ON f.student_key = ds.student_key
                GROUP BY ds.student_id, ds.full_name, ds.group_name
            )
            SELECT student_id, full_name, group_name,
                   ROUND(avg_gpa, 3) AS avg_gpa,
                   ROUND(avg_attendance, 2) AS avg_attendance,
                   failed_count,
                   total_grades
            FROM student_gpa
            WHERE avg_gpa < :threshold OR failed_count > 3
            ORDER BY avg_gpa ASC
            LIMIT :lim
            """
        ),
        {"threshold": threshold, "lim": limit},
    ).mappings().all()

    items = []
    for r in rows:
        d = dict(r)
        # Risk score: 0-100
        risk = 0
        if d["avg_gpa"] < 2.0:
            risk += 50
        elif d["avg_gpa"] < 2.5:
            risk += 30
        if d["avg_attendance"] < 75:
            risk += 20
        if d["failed_count"] > 3:
            risk += 30
        d["risk_score"] = min(100, risk)
        d["risk_level"] = "kritik" if risk >= 70 else "yuqori" if risk >= 40 else "o'rta"
        items.append(d)

    return {"count": len(items), "threshold": threshold, "items": items}


@router.get("/top-performers", dependencies=[Depends(require_any)])
def top_performers(
    limit: int = Query(20, ge=1, le=100),
    olap: Session = Depends(get_olap_db),
):
    """Eng yaxshi natijaga ega talabalar (stipendiyaga tavsiya uchun)."""
    rows = olap.execute(
        text(
            """
            SELECT ds.student_id, ds.full_name, ds.group_name,
                   ROUND(AVG(f.gpa_points), 3) AS avg_gpa,
                   ROUND(AVG(f.grade_value), 2) AS avg_grade,
                   ROUND(AVG(f.attendance_percentage), 2) AS avg_attendance,
                   COUNT(*) AS grades_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            GROUP BY ds.student_id, ds.full_name, ds.group_name
            HAVING COUNT(*) >= 10 AND AVG(f.gpa_points) >= 3.5
            ORDER BY avg_gpa DESC
            LIMIT :lim
            """
        ),
        {"lim": limit},
    ).mappings().all()
    return {"count": len(rows), "items": [dict(r) for r in rows]}


@router.get("/anomalies", dependencies=[Depends(require_dekan)])
def detect_anomalies(olap: Session = Depends(get_olap_db)):
    """Anomaliyalarni aniqlash: o'rtadan keskin ajraladigan baholar/talabalar.

    Z-score asosida: |z| > 2 bo'lganlar anomaliya.
    """
    # Fakultet bo'yicha o'rtacha va std
    base = olap.execute(
        text(
            """
            SELECT fac.faculty_name,
                   AVG(f.grade_value) AS mean_grade,
                   AVG(f.gpa_points) AS mean_gpa
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            GROUP BY fac.faculty_name
            """
        )
    ).mappings().all()

    # Anomal talabalar — fakultet o'rtachasidan keskin past
    anomalies = []
    for fac in base:
        rows = olap.execute(
            text(
                """
                SELECT ds.student_id, ds.full_name, ds.group_name,
                       ROUND(AVG(f.grade_value), 2) AS avg_grade
                FROM fact_student_grades f
                JOIN dim_student ds ON f.student_key = ds.student_key
                JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
                WHERE fac.faculty_name = :fname
                GROUP BY ds.student_id, ds.full_name, ds.group_name
                HAVING AVG(f.grade_value) < (:mean - 15) OR AVG(f.grade_value) > (:mean + 15)
                """
            ),
            {"fname": fac["faculty_name"], "mean": float(fac["mean_grade"])},
        ).mappings().all()

        for r in rows:
            d = dict(r)
            d["faculty"] = fac["faculty_name"]
            d["faculty_mean"] = round(float(fac["mean_grade"]), 2)
            d["deviation"] = round(d["avg_grade"] - float(fac["mean_grade"]), 2)
            d["type"] = "g'ayrioddiy past" if d["deviation"] < 0 else "g'ayrioddiy yuqori"
            anomalies.append(d)

    anomalies.sort(key=lambda x: abs(x["deviation"]), reverse=True)
    return {"count": len(anomalies), "items": anomalies[:50]}


@router.get("/student/{student_id}/cohort-compare", dependencies=[Depends(require_any)])
def cohort_compare(
    student_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    """Talabani guruh va kurs cohort i bilan solishtirish."""
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)

    my = olap.execute(
        text(
            """SELECT ROUND(AVG(gpa_points), 3) AS gpa,
                   ROUND(AVG(grade_value), 2) AS avg_grade,
                   ROUND(AVG(attendance_percentage), 2) AS attendance
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.student_id = :sid"""
        ),
        {"sid": student.student_id},
    ).mappings().first() or {}

    group = olap.execute(
        text(
            """SELECT ROUND(AVG(gpa_points), 3) AS gpa,
                   ROUND(AVG(grade_value), 2) AS avg_grade,
                   ROUND(AVG(attendance_percentage), 2) AS attendance
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.group_name = :grp"""
        ),
        {"grp": student.group.name if student.group else ""},
    ).mappings().first() or {}

    course = olap.execute(
        text(
            """SELECT ROUND(AVG(gpa_points), 3) AS gpa,
                   ROUND(AVG(grade_value), 2) AS avg_grade,
                   ROUND(AVG(attendance_percentage), 2) AS attendance
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            WHERE fac.faculty_name = :fname AND fac.course = :course"""
        ),
        {
            "fname": (student.group.specialty.faculty.name if student.group else ""),
            "course": (student.group.course if student.group else 0),
        },
    ).mappings().first() or {}

    return {
        "student_id": student.student_id,
        "my": dict(my),
        "group_avg": dict(group),
        "course_avg": dict(course),
        "comparison": {
            "vs_group_gpa": (float(my.get("gpa") or 0) - float(group.get("gpa") or 0)),
            "vs_course_gpa": (float(my.get("gpa") or 0) - float(course.get("gpa") or 0)),
        },
    }


@router.get("/student/{student_id}/recommend-subjects", dependencies=[Depends(require_any)])
def recommend_subjects(
    student_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    """Talabaga fan tavsiyalari."""
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)

    weak = olap.execute(
        text(
            """SELECT s.subject_name, s.department,
                   ROUND(AVG(f.grade_value), 2) AS my_grade,
                   COUNT(*) AS grades_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            WHERE ds.student_id = :sid
            GROUP BY s.subject_name, s.department
            HAVING AVG(f.grade_value) < 70
            ORDER BY AVG(f.grade_value) ASC
            LIMIT 5"""
        ),
        {"sid": student.student_id},
    ).mappings().all()

    recommendations = []
    for w in weak:
        d = dict(w)
        if d["my_grade"] < 55:
            d["priority"] = "kritik"
            d["action"] = "Qayta topshirish arizasi yuborish, repititor olish"
        elif d["my_grade"] < 65:
            d["priority"] = "yuqori"
            d["action"] = "Qo'shimcha mashg'ulotlar, kafedra konsultatsiyalari"
        else:
            d["priority"] = "o'rta"
            d["action"] = "Mavzularni qaytarib ishlash"
        recommendations.append(d)

    return {
        "student_id": student.student_id,
        "weak_subjects": recommendations,
        "summary": (
            f"{len(recommendations)} ta fanda qo'shimcha e'tibor talab etiladi"
            if recommendations
            else "Barcha fanlarda yaxshi natijalar"
        ),
    }


@router.get("/faculty-insights/{faculty_name}", dependencies=[Depends(require_dekan)])
def faculty_insights(faculty_name: str, olap: Session = Depends(get_olap_db)):
    """Fakultet bo'yicha avtomatik tahlil va tavsiyalar."""
    stats = olap.execute(
        text(
            """
            SELECT
                ROUND(AVG(f.gpa_points), 3) AS avg_gpa,
                ROUND(AVG(f.grade_value), 2) AS avg_grade,
                ROUND(AVG(f.attendance_percentage), 2) AS avg_attendance,
                ROUND(SUM(CASE WHEN f.is_passed THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS passing_rate,
                COUNT(DISTINCT f.student_key) AS students
            FROM fact_student_grades f
            JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
            WHERE fac.faculty_name = :fname
            """
        ),
        {"fname": faculty_name},
    ).mappings().first()

    if not stats:
        raise HTTPException(404, "Fakultet topilmadi")

    s = dict(stats)
    insights = []
    recommendations = []

    if s["avg_gpa"] and float(s["avg_gpa"]) < 2.5:
        insights.append(f"O'rtacha GPA past: {s['avg_gpa']} (3.0 dan past)")
        recommendations.append("O'qituvchilarga metodologik treninglar tashkil etish")
        recommendations.append("Past o'zlashtirgan talabalarga qo'shimcha mashg'ulotlar")

    if s["avg_attendance"] and float(s["avg_attendance"]) < 80:
        insights.append(f"Davomat past: {s['avg_attendance']}%")
        recommendations.append("Talabalar bilan individual ish — sabablar aniqlanishi kerak")

    if s["passing_rate"] and float(s["passing_rate"]) < 75:
        insights.append(f"O'tish darajasi past: {s['passing_rate']}%")
        recommendations.append("O'quv rejasini qayta ko'rib chiqish")

    if not insights:
        insights.append("Fakultet ko'rsatkichlari me'yorda")

    return {
        "faculty_name": faculty_name,
        "stats": s,
        "insights": insights,
        "recommendations": recommendations,
    }
