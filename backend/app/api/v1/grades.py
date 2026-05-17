"""Baholar CRUD endpointlari."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_any, require_teacher
from app.database import get_oltp_db
from app.models.oltp.grade import AssessmentType, Grade
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.grade import (
    AssessmentTypeCreate,
    AssessmentTypeResponse,
    GradeCreate,
    GradeResponse,
    GradeUpdate,
)
from app.services.crud_base import CRUDBase

router = APIRouter(prefix="/grades", tags=["Grades"])

crud = CRUDBase[Grade, GradeCreate, GradeUpdate](Grade, "Baho")


@router.get("", response_model=PaginatedResponse[GradeResponse], dependencies=[Depends(require_any)])
def list_grades(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    student_id: int | None = None,
    subject_id: int | None = None,
    academic_year: str | None = None,
    db: Session = Depends(get_oltp_db),
):
    return crud.list(
        db,
        page,
        page_size,
        filters={"student_id": student_id, "subject_id": subject_id, "academic_year": academic_year},
    )


@router.get("/{grade_id}", response_model=GradeResponse, dependencies=[Depends(require_any)])
def get_grade(grade_id: int, db: Session = Depends(get_oltp_db)):
    return crud.get(db, grade_id)


@router.post(
    "",
    response_model=GradeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_teacher)],
)
def create_grade(payload: GradeCreate, db: Session = Depends(get_oltp_db)):
    return crud.create(db, payload)


@router.put("/{grade_id}", response_model=GradeResponse, dependencies=[Depends(require_teacher)])
def update_grade(grade_id: int, payload: GradeUpdate, db: Session = Depends(get_oltp_db)):
    return crud.update(db, grade_id, payload)


@router.delete("/{grade_id}", response_model=MessageResponse, dependencies=[Depends(require_teacher)])
def delete_grade(grade_id: int, db: Session = Depends(get_oltp_db)):
    crud.delete(db, grade_id)
    return MessageResponse(message="Baho o'chirildi")


# Baholash turlari
@router.get("/assessment-types/all", response_model=list[AssessmentTypeResponse], dependencies=[Depends(require_any)])
def list_assessment_types(db: Session = Depends(get_oltp_db)):
    return db.query(AssessmentType).all()


@router.post(
    "/assessment-types",
    response_model=AssessmentTypeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_teacher)],
)
def create_assessment_type(payload: AssessmentTypeCreate, db: Session = Depends(get_oltp_db)):
    obj = AssessmentType(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
