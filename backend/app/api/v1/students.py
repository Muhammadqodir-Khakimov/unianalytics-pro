"""Talabalar CRUD endpointlari."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_any, require_dekan
from app.database import get_oltp_db
from app.models.oltp.student import Student
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services.crud_base import CRUDBase

router = APIRouter(prefix="/students", tags=["Students"])

crud = CRUDBase[Student, StudentCreate, StudentUpdate](Student, "Talaba")


@router.get("", response_model=PaginatedResponse[StudentResponse], dependencies=[Depends(require_any)])
def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    group_id: int | None = None,
    enrollment_year: int | None = None,
    db: Session = Depends(get_oltp_db),
):
    return crud.list(db, page, page_size, filters={"group_id": group_id, "enrollment_year": enrollment_year})


@router.get("/{student_id}", response_model=StudentResponse, dependencies=[Depends(require_any)])
def get_student(student_id: int, db: Session = Depends(get_oltp_db)):
    return crud.get(db, student_id)


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_dekan)],
)
def create_student(payload: StudentCreate, db: Session = Depends(get_oltp_db)):
    return crud.create(db, payload)


@router.put("/{student_id}", response_model=StudentResponse, dependencies=[Depends(require_dekan)])
def update_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_oltp_db)):
    return crud.update(db, student_id, payload)


@router.delete("/{student_id}", response_model=MessageResponse, dependencies=[Depends(require_dekan)])
def delete_student(student_id: int, db: Session = Depends(get_oltp_db)):
    crud.delete(db, student_id)
    return MessageResponse(message="Talaba o'chirildi")
