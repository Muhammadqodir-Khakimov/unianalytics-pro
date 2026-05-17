"""Stipendiya hisoblash endpointlari.

Real universitet qoidasi (taqribiy):
- GPA ≥ 3.5: A'lo (1.25x asosiy stipendiya)
- GPA ≥ 3.0: Yaxshi (1.0x asosiy stipendiya)
- GPA ≥ 2.5: Qoniqarli (0.7x asosiy stipendiya)
- GPA < 2.5: Stipendiyasiz
- Qarz fanlar bo'lsa — stipendiya berilmaydi
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import require_any, require_dekan
from app.database import get_olap_db, get_oltp_db
from app.models.oltp.student import Student

router = APIRouter(prefix="/scholarship", tags=["Stipendiya"])

BASE_AMOUNT = 1_000_000  # so'm — asosiy stipendiya


def _calculate(gpa: float | None, has_failed: bool) -> dict:
    """Bitta talaba uchun stipendiya hisoblash."""
    if gpa is None:
        return {"eligible": False, "amount": 0, "tier": "no_data", "reason": "Baholar yo'q"}
    if has_failed:
        return {"eligible": False, "amount": 0, "tier": "failed", "reason": "Qarz fanlar mavjud"}
    if gpa >= 3.5:
        return {"eligible": True, "amount": int(BASE_AMOUNT * 1.25), "tier": "excellent", "reason": "A'lo natija"}
    if gpa >= 3.0:
        return {"eligible": True, "amount": int(BASE_AMOUNT * 1.0), "tier": "good", "reason": "Yaxshi natija"}
    if gpa >= 2.5:
        return {"eligible": True, "amount": int(BASE_AMOUNT * 0.7), "tier": "satisfactory", "reason": "Qoniqarli"}
    return {"eligible": False, "amount": 0, "tier": "insufficient", "reason": "GPA past"}


@router.get("/student/{student_id}", dependencies=[Depends(require_any)])
def student_scholarship(
    student_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    """Bitta talaba uchun stipendiya holatini hisoblash."""
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)

    row = olap.execute(
        text(
            """
            SELECT ROUND(AVG(gpa_points), 3) AS gpa,
                   SUM(CASE WHEN is_passed THEN 0 ELSE 1 END) AS failed_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.student_id = :sid
            """
        ),
        {"sid": student.student_id},
    ).mappings().first() or {}

    gpa = float(row["gpa"]) if row.get("gpa") else None
    has_failed = bool(row.get("failed_count") and int(row["failed_count"]) > 0)
    calc = _calculate(gpa, has_failed)

    return {
        "student_id": student.id,
        "student_code": student.student_id,
        "full_name": student.full_name,
        "group_name": student.group.name if student.group else None,
        "gpa": gpa,
        "failed_count": int(row.get("failed_count") or 0),
        **calc,
    }


@router.get("/group/{group_name}", dependencies=[Depends(require_dekan)])
def group_scholarships(group_name: str, olap: Session = Depends(get_olap_db)):
    """Guruh bo'yicha barcha talabalar stipendiyasi."""
    rows = olap.execute(
        text(
            """
            SELECT ds.student_id, ds.full_name, ds.group_name,
                   ROUND(AVG(f.gpa_points), 3) AS gpa,
                   SUM(CASE WHEN f.is_passed THEN 0 ELSE 1 END) AS failed_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.group_name = :grp
            GROUP BY ds.student_id, ds.full_name, ds.group_name
            ORDER BY gpa DESC
            """
        ),
        {"grp": group_name},
    ).mappings().all()

    items = []
    total_amount = 0
    eligible_count = 0
    for r in rows:
        gpa = float(r["gpa"]) if r["gpa"] else None
        has_failed = bool(r["failed_count"] and int(r["failed_count"]) > 0)
        calc = _calculate(gpa, has_failed)
        items.append({**dict(r), **calc})
        total_amount += calc["amount"]
        if calc["eligible"]:
            eligible_count += 1

    return {
        "group_name": group_name,
        "total_students": len(items),
        "eligible_count": eligible_count,
        "total_amount": total_amount,
        "items": items,
    }


@router.get("/summary", dependencies=[Depends(require_dekan)])
def scholarship_summary(olap: Session = Depends(get_olap_db)):
    """Umumiy stipendiya statistika (barcha talabalar)."""
    rows = olap.execute(
        text(
            """
            SELECT ds.student_id, ds.full_name, ds.group_name,
                   ROUND(AVG(f.gpa_points), 3) AS gpa,
                   SUM(CASE WHEN f.is_passed THEN 0 ELSE 1 END) AS failed_count
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            GROUP BY ds.student_id, ds.full_name, ds.group_name
            """
        )
    ).mappings().all()

    by_tier: dict[str, dict] = {
        "excellent": {"count": 0, "amount": 0},
        "good": {"count": 0, "amount": 0},
        "satisfactory": {"count": 0, "amount": 0},
        "insufficient": {"count": 0, "amount": 0},
        "failed": {"count": 0, "amount": 0},
        "no_data": {"count": 0, "amount": 0},
    }

    total_amount = 0
    for r in rows:
        gpa = float(r["gpa"]) if r["gpa"] else None
        has_failed = bool(r["failed_count"] and int(r["failed_count"]) > 0)
        calc = _calculate(gpa, has_failed)
        by_tier[calc["tier"]]["count"] += 1
        by_tier[calc["tier"]]["amount"] += calc["amount"]
        total_amount += calc["amount"]

    return {
        "total_students": len(rows),
        "total_monthly_amount": total_amount,
        "by_tier": by_tier,
        "base_amount": BASE_AMOUNT,
    }
