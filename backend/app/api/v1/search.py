"""Global qidiruv endpointi — talaba/o'qituvchi/fan bo'yicha."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.dependencies import require_any
from app.database import get_oltp_db
from app.models.oltp.student import Student
from app.models.oltp.subject import Subject
from app.models.oltp.teacher import Teacher

router = APIRouter(prefix="/search", tags=["Search"], dependencies=[Depends(require_any)])


@router.get("")
def global_search(
    q: str = Query(..., min_length=2, description="Qidiruv so'rovi"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_oltp_db),
):
    """Talaba, o'qituvchi, fan va fakultet bo'yicha qidiruv."""
    pattern = f"%{q}%"

    students = (
        db.query(Student)
        .filter(or_(Student.full_name.ilike(pattern), Student.student_id.ilike(pattern)))
        .limit(limit)
        .all()
    )
    teachers = (
        db.query(Teacher)
        .filter(or_(Teacher.full_name.ilike(pattern), Teacher.teacher_id.ilike(pattern)))
        .limit(limit)
        .all()
    )
    subjects = (
        db.query(Subject)
        .filter(or_(Subject.name.ilike(pattern), Subject.code.ilike(pattern)))
        .limit(limit)
        .all()
    )

    return {
        "query": q,
        "students": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "full_name": s.full_name,
                "group_name": s.group.name if s.group else None,
                "type": "student",
                "link": f"/students/{s.id}",
            }
            for s in students
        ],
        "teachers": [
            {
                "id": t.id,
                "teacher_id": t.teacher_id,
                "full_name": t.full_name,
                "department": t.department,
                "type": "teacher",
                "link": f"/teachers/{t.id}",
            }
            for t in teachers
        ],
        "subjects": [
            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "department": s.department,
                "type": "subject",
                "link": f"/subjects/{s.id}",
            }
            for s in subjects
        ],
        "total": len(students) + len(teachers) + len(subjects),
    }
