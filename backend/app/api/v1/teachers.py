"""O'qituvchilar CRUD endpointlari."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin, require_any
from app.database import get_oltp_db
from app.models.oltp.teacher import Teacher
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
from app.services.crud_base import CRUDBase

router = APIRouter(prefix="/teachers", tags=["Teachers"])

crud = CRUDBase[Teacher, TeacherCreate, TeacherUpdate](Teacher, "O'qituvchi")


@router.get("", response_model=PaginatedResponse[TeacherResponse], dependencies=[Depends(require_any)])
def list_teachers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    department: str | None = None,
    db: Session = Depends(get_oltp_db),
):
    return crud.list(db, page, page_size, filters={"department": department})


@router.get("/{teacher_id}", response_model=TeacherResponse, dependencies=[Depends(require_any)])
def get_teacher(teacher_id: int, db: Session = Depends(get_oltp_db)):
    return crud.get(db, teacher_id)


@router.post(
    "",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_teacher(payload: TeacherCreate, db: Session = Depends(get_oltp_db)):
    return crud.create(db, payload)


@router.put("/{teacher_id}", response_model=TeacherResponse, dependencies=[Depends(require_admin)])
def update_teacher(teacher_id: int, payload: TeacherUpdate, db: Session = Depends(get_oltp_db)):
    return crud.update(db, teacher_id, payload)


@router.delete("/{teacher_id}", response_model=MessageResponse, dependencies=[Depends(require_admin)])
def delete_teacher(teacher_id: int, db: Session = Depends(get_oltp_db)):
    crud.delete(db, teacher_id)
    return MessageResponse(message="O'qituvchi o'chirildi")
