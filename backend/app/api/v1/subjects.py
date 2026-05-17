"""Fanlar CRUD endpointlari."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin, require_any
from app.database import get_oltp_db
from app.models.oltp.subject import Subject
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.services.crud_base import CRUDBase

router = APIRouter(prefix="/subjects", tags=["Subjects"])

crud = CRUDBase[Subject, SubjectCreate, SubjectUpdate](Subject, "Fan")


@router.get("", response_model=PaginatedResponse[SubjectResponse], dependencies=[Depends(require_any)])
def list_subjects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    department: str | None = None,
    semester: int | None = None,
    db: Session = Depends(get_oltp_db),
):
    return crud.list(db, page, page_size, filters={"department": department, "semester": semester})


@router.get("/{subject_id}", response_model=SubjectResponse, dependencies=[Depends(require_any)])
def get_subject(subject_id: int, db: Session = Depends(get_oltp_db)):
    return crud.get(db, subject_id)


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_oltp_db)):
    return crud.create(db, payload)


@router.put("/{subject_id}", response_model=SubjectResponse, dependencies=[Depends(require_admin)])
def update_subject(subject_id: int, payload: SubjectUpdate, db: Session = Depends(get_oltp_db)):
    return crud.update(db, subject_id, payload)


@router.delete("/{subject_id}", response_model=MessageResponse, dependencies=[Depends(require_admin)])
def delete_subject(subject_id: int, db: Session = Depends(get_oltp_db)):
    crud.delete(db, subject_id)
    return MessageResponse(message="Fan o'chirildi")
