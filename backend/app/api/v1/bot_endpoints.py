"""Telegram bot-ga oid endpointlar (TZ 4.2.4) — production (OLTP).

Endpointlar:
- POST  /bot/link-parent      — ota-onaning farzandiga bog'lanish so'rovi
- POST  /bot/link-parent/{id}/approve — talaba so'rovni tasdiqlaydi
- POST  /bot/link-parent/{id}/reject  — talaba so'rovni rad etadi
- GET   /bot/parent-links     — joriy foydalanuvchining bog'lanishlari
- PATCH /users/me/digest      — haftalik dayjest yoqish/o'chirish
- GET   /users/me/preferences — barcha foydalanuvchi sozlamalari
- GET   /my/contacts          — kurator/dekan/kafedra mudiri kontaktlari
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_oltp_db
from app.models.oltp.faculty import Group
from app.models.oltp.parent_link import (
    ParentLink,
    ParentLinkStatus,
    UserPreferences,
)
from app.models.oltp.student import Student
from app.models.oltp.teacher import Teacher
from app.models.oltp.user import User, UserRole

router = APIRouter(tags=["Telegram bot (TZ)"])


# ---------------------------------------------------------------------------
# Pydantic sxemalar
# ---------------------------------------------------------------------------
class LinkParentRequest(BaseModel):
    talaba_hemis_id: str = Field(..., min_length=1, max_length=32, examples=["11220194"])
    note: str | None = Field(None, max_length=256)


class ParentLinkOut(BaseModel):
    id: int
    parent_user_id: int
    student_id: int
    student_full_name: str
    student_hemis_id: str
    status: ParentLinkStatus
    requested_at: datetime
    decided_at: datetime | None = None

    model_config = {"from_attributes": True}


class DecisionRequest(BaseModel):
    note: str | None = None


class PreferencesOut(BaseModel):
    user_id: int
    weekly_digest_enabled: bool
    notify_new_grade: bool
    notify_academic_risk: bool
    language: str

    model_config = {"from_attributes": True}


class DigestUpdate(BaseModel):
    weekly_digest_enabled: bool


class PreferencesUpdate(BaseModel):
    weekly_digest_enabled: bool | None = None
    notify_new_grade: bool | None = None
    notify_academic_risk: bool | None = None
    language: Literal["uz_lat", "uz_cyr", "ru"] | None = None


class ContactRow(BaseModel):
    fish: str
    phone: str | None = None
    email: str | None = None
    role: str


class ContactsResponse(BaseModel):
    kurator: ContactRow | None = None
    dekan: ContactRow | None = None
    kafedra_mudiri: ContactRow | None = None


# ---------------------------------------------------------------------------
# Yordamchilar
# ---------------------------------------------------------------------------
def _get_or_create_prefs(oltp: Session, user_id: int) -> UserPreferences:
    prefs = (
        oltp.query(UserPreferences)
        .filter(UserPreferences.user_id == user_id)
        .first()
    )
    if prefs is None:
        prefs = UserPreferences(user_id=user_id)
        oltp.add(prefs)
        oltp.flush()
    return prefs


def _serialize_link(link: ParentLink, student: Student) -> ParentLinkOut:
    return ParentLinkOut(
        id=link.id,
        parent_user_id=link.parent_user_id,
        student_id=link.student_id,
        student_full_name=student.full_name,
        student_hemis_id=student.student_id,
        status=link.status,
        requested_at=link.requested_at,
        decided_at=link.decided_at,
    )


def _current_student(user: User, oltp: Session) -> Student | None:
    if user.role != UserRole.STUDENT:
        return None
    return (
        oltp.query(Student)
        .filter((Student.user_id == user.id) | (Student.email == user.email))
        .first()
    )


# ---------------------------------------------------------------------------
# POST /bot/link-parent
# ---------------------------------------------------------------------------
@router.post(
    "/bot/link-parent",
    response_model=ParentLinkOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_parent_link(
    payload: LinkParentRequest,
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> ParentLinkOut:
    student = (
        oltp.query(Student)
        .filter(Student.student_id == payload.talaba_hemis_id)
        .first()
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"HEMIS ID {payload.talaba_hemis_id} bo'yicha talaba topilmadi",
        )

    existing = (
        oltp.query(ParentLink)
        .filter(
            ParentLink.parent_user_id == user.id,
            ParentLink.student_id == student.id,
        )
        .first()
    )
    if existing:
        if existing.status == ParentLinkStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bu talabaga allaqachon bog'langansiz",
            )
        if existing.status == ParentLinkStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="So'rov allaqachon yuborilgan, talabaning javobini kuting",
            )
        # rejected/revoked → qayta so'rov yuborishga ruxsat (state qayta tiklash)
        existing.status = ParentLinkStatus.PENDING
        existing.requested_at = datetime.utcnow()
        existing.decided_at = None
        existing.decided_by_student = False
        existing.note = payload.note
        link = existing
    else:
        link = ParentLink(
            parent_user_id=user.id,
            student_id=student.id,
            status=ParentLinkStatus.PENDING,
            note=payload.note,
        )
        oltp.add(link)

    oltp.commit()
    oltp.refresh(link)
    return _serialize_link(link, student)


# ---------------------------------------------------------------------------
# POST /bot/link-parent/{id}/approve | /reject  — talaba qarori
# ---------------------------------------------------------------------------
def _decide_link(
    link_id: int,
    new_status: ParentLinkStatus,
    user: User,
    oltp: Session,
    note: str | None,
) -> ParentLinkOut:
    student = _current_student(user, oltp)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faqat talabalar bog'lanish so'rovlariga qaror qabul qilishi mumkin",
        )

    link = oltp.query(ParentLink).filter(ParentLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="So'rov topilmadi")
    if link.student_id != student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu so'rov sizga tegishli emas",
        )
    if link.status != ParentLinkStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"So'rov holati '{link.status.value}' — qayta qaror qabul qilib bo'lmaydi",
        )

    link.status = new_status
    link.decided_at = datetime.utcnow()
    link.decided_by_student = True
    if note:
        link.note = note
    oltp.commit()
    oltp.refresh(link)
    return _serialize_link(link, student)


@router.post("/bot/link-parent/{link_id}/approve", response_model=ParentLinkOut)
def approve_link(
    link_id: int,
    payload: DecisionRequest = Body(default_factory=DecisionRequest),
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> ParentLinkOut:
    return _decide_link(link_id, ParentLinkStatus.APPROVED, user, oltp, payload.note)


@router.post("/bot/link-parent/{link_id}/reject", response_model=ParentLinkOut)
def reject_link(
    link_id: int,
    payload: DecisionRequest = Body(default_factory=DecisionRequest),
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> ParentLinkOut:
    return _decide_link(link_id, ParentLinkStatus.REJECTED, user, oltp, payload.note)


# ---------------------------------------------------------------------------
# GET /bot/parent-links — joriy foydalanuvchining bog'lanishlari
# ---------------------------------------------------------------------------
@router.get("/bot/parent-links", response_model=list[ParentLinkOut])
def list_my_parent_links(
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> list[ParentLinkOut]:
    """Ota-ona uchun: o'z so'rovlari. Talaba uchun: o'ziga kelgan so'rovlar."""
    query = oltp.query(ParentLink, Student).join(Student, Student.id == ParentLink.student_id)
    student = _current_student(user, oltp)
    if student is not None:
        query = query.filter(ParentLink.student_id == student.id)
    else:
        query = query.filter(ParentLink.parent_user_id == user.id)

    return [_serialize_link(link, student) for link, student in query.all()]


# ---------------------------------------------------------------------------
# PATCH /users/me/digest
# ---------------------------------------------------------------------------
@router.patch("/users/me/digest", response_model=PreferencesOut)
def set_weekly_digest(
    payload: DigestUpdate = Body(...),
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> PreferencesOut:
    prefs = _get_or_create_prefs(oltp, user.id)
    prefs.weekly_digest_enabled = payload.weekly_digest_enabled
    oltp.commit()
    oltp.refresh(prefs)
    return PreferencesOut.model_validate(prefs)


# ---------------------------------------------------------------------------
# GET / PATCH /users/me/preferences  — to'liq sozlamalar
# ---------------------------------------------------------------------------
@router.get("/users/me/preferences", response_model=PreferencesOut)
def get_preferences(
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> PreferencesOut:
    prefs = _get_or_create_prefs(oltp, user.id)
    oltp.commit()
    return PreferencesOut.model_validate(prefs)


@router.patch("/users/me/preferences", response_model=PreferencesOut)
def update_preferences(
    payload: PreferencesUpdate = Body(...),
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> PreferencesOut:
    prefs = _get_or_create_prefs(oltp, user.id)
    if payload.weekly_digest_enabled is not None:
        prefs.weekly_digest_enabled = payload.weekly_digest_enabled
    if payload.notify_new_grade is not None:
        prefs.notify_new_grade = payload.notify_new_grade
    if payload.notify_academic_risk is not None:
        prefs.notify_academic_risk = payload.notify_academic_risk
    if payload.language is not None:
        prefs.language = payload.language
    oltp.commit()
    oltp.refresh(prefs)
    return PreferencesOut.model_validate(prefs)


# ---------------------------------------------------------------------------
# GET /my/contacts
# ---------------------------------------------------------------------------
@router.get("/my/contacts", response_model=ContactsResponse)
def my_contacts(
    user: User = Depends(get_current_user),
    oltp: Session = Depends(get_oltp_db),
) -> ContactsResponse:
    """Joriy talabaning kurator / dekan / kafedra mudiri kontaktlari (TZ 4.2.4 /aloqa)."""
    resp = ContactsResponse()

    student = _current_student(user, oltp)
    if not student or not student.group_id:
        return resp

    group: Group | None = oltp.query(Group).filter(Group.id == student.group_id).first()
    if not group:
        return resp

    department_name = (
        group.specialty.faculty.name
        if group.specialty and group.specialty.faculty
        else None
    )

    if department_name:
        kurator = (
            oltp.query(Teacher)
            .filter(Teacher.department == department_name)
            .first()
        )
        if kurator:
            resp.kurator = ContactRow(
                fish=kurator.full_name,
                phone=kurator.phone,
                email=kurator.email,
                role="kurator",
            )

    dekan_user = (
        oltp.query(User)
        .filter(User.role == UserRole.DEKAN)
        .first()
    )
    if dekan_user:
        resp.dekan = ContactRow(
            fish=dekan_user.full_name,
            email=dekan_user.email,
            phone=None,
            role="dekan",
        )

    return resp
