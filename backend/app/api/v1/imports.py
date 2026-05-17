"""CSV bulk import endpointlari — baholarni Excel/CSV dan yuklash."""
import csv
import io
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import require_teacher
from app.database import get_oltp_db
from app.models.oltp.grade import AssessmentType, Grade
from app.models.oltp.student import Student
from app.models.oltp.subject import Subject

router = APIRouter(prefix="/imports", tags=["Import"], dependencies=[Depends(require_teacher)])


@router.post("/grades/csv")
async def import_grades_csv(
    teacher_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_oltp_db),
):
    """CSV fayldan ommaviy baho yuklash.

    Format (header bilan):
        student_id,subject_code,assessment_type,grade_value,attendance,semester,academic_year,grade_date

    Misol:
        ST202500001,INF001,JN,87.5,95,kuzgi,2024-2025,2024-11-15
    """
    if not file.filename.endswith((".csv", ".txt")):
        raise HTTPException(400, "Faqat CSV fayl qabul qilinadi")

    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    inserted = 0
    errors: list[dict] = []
    row_num = 1

    # Pre-cache lookup mappings
    students_by_sid = {s.student_id: s.id for s in db.query(Student).all()}
    subjects_by_code = {s.code: s.id for s in db.query(Subject).all()}
    assessment_by_name = {a.name: a.id for a in db.query(AssessmentType).all()}

    for row in reader:
        row_num += 1
        try:
            sid = row.get("student_id", "").strip()
            scode = row.get("subject_code", "").strip()
            atype = row.get("assessment_type", "").strip()

            if sid not in students_by_sid:
                errors.append({"row": row_num, "error": f"Talaba topilmadi: {sid}"})
                continue
            if scode not in subjects_by_code:
                errors.append({"row": row_num, "error": f"Fan topilmadi: {scode}"})
                continue
            if atype not in assessment_by_name:
                errors.append({"row": row_num, "error": f"Baholash turi topilmadi: {atype}"})
                continue

            grade_value = float(row["grade_value"])
            attendance = float(row.get("attendance", 100))
            grade_date = datetime.strptime(row["grade_date"], "%Y-%m-%d").date()

            grade = Grade(
                student_id=students_by_sid[sid],
                subject_id=subjects_by_code[scode],
                teacher_id=teacher_id,
                assessment_type_id=assessment_by_name[atype],
                grade_value=grade_value,
                attendance_percentage=attendance,
                is_passed=grade_value >= 55,
                semester=row.get("semester", "kuzgi"),
                academic_year=row.get("academic_year", "2024-2025"),
                grade_date=grade_date,
            )
            db.add(grade)
            inserted += 1
        except Exception as e:
            errors.append({"row": row_num, "error": str(e)})

    db.commit()

    return {
        "inserted": inserted,
        "errors_count": len(errors),
        "errors": errors[:50],  # birinchi 50 xato
    }


@router.get("/grades/csv/template")
def csv_template():
    """CSV import uchun namuna fayl."""
    sample = (
        "student_id,subject_code,assessment_type,grade_value,attendance,semester,academic_year,grade_date\n"
        "ST202500001,INF001,JN,87.5,95,kuzgi,2024-2025,2024-11-15\n"
        "ST202500002,INF001,JN,72.0,90,kuzgi,2024-2025,2024-11-15\n"
    )
    from fastapi.responses import Response

    return Response(
        sample,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="grades_template.csv"'},
    )
