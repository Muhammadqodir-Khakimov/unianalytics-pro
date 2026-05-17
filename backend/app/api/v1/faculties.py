"""Fakultetlar CRUD endpointlari."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin, require_any
from app.database import get_oltp_db
from app.models.oltp.faculty import Faculty, Group, Specialty
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.faculty import (
    FacultyCreate,
    FacultyResponse,
    FacultyUpdate,
    GroupCreate,
    GroupResponse,
    SpecialtyCreate,
    SpecialtyResponse,
)
from app.services.crud_base import CRUDBase

router = APIRouter(prefix="/faculties", tags=["Faculties"])

faculty_crud = CRUDBase[Faculty, FacultyCreate, FacultyUpdate](Faculty, "Fakultet")
specialty_crud = CRUDBase[Specialty, SpecialtyCreate, SpecialtyCreate](Specialty, "Yo'nalish")
group_crud = CRUDBase[Group, GroupCreate, GroupCreate](Group, "Guruh")


@router.get("", response_model=PaginatedResponse[FacultyResponse], dependencies=[Depends(require_any)])
def list_faculties(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_oltp_db),
):
    return faculty_crud.list(db, page, page_size)


@router.get("/{faculty_id}", response_model=FacultyResponse, dependencies=[Depends(require_any)])
def get_faculty(faculty_id: int, db: Session = Depends(get_oltp_db)):
    return faculty_crud.get(db, faculty_id)


@router.post(
    "",
    response_model=FacultyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_faculty(payload: FacultyCreate, db: Session = Depends(get_oltp_db)):
    return faculty_crud.create(db, payload)


@router.put("/{faculty_id}", response_model=FacultyResponse, dependencies=[Depends(require_admin)])
def update_faculty(faculty_id: int, payload: FacultyUpdate, db: Session = Depends(get_oltp_db)):
    return faculty_crud.update(db, faculty_id, payload)


@router.delete("/{faculty_id}", response_model=MessageResponse, dependencies=[Depends(require_admin)])
def delete_faculty(faculty_id: int, db: Session = Depends(get_oltp_db)):
    faculty_crud.delete(db, faculty_id)
    return MessageResponse(message="Fakultet o'chirildi")


# Specialty endpointlari
@router.get("/specialties/all", response_model=list[SpecialtyResponse], dependencies=[Depends(require_any)])
def list_specialties(db: Session = Depends(get_oltp_db)):
    return db.query(Specialty).all()


@router.post(
    "/specialties",
    response_model=SpecialtyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_specialty(payload: SpecialtyCreate, db: Session = Depends(get_oltp_db)):
    return specialty_crud.create(db, payload)


# Group endpointlari
@router.get("/groups/all", response_model=list[GroupResponse], dependencies=[Depends(require_any)])
def list_groups(db: Session = Depends(get_oltp_db)):
    return db.query(Group).all()


@router.post(
    "/groups",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_group(payload: GroupCreate, db: Session = Depends(get_oltp_db)):
    return group_crud.create(db, payload)
