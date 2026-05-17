"""Foydalanuvchi profil va boshqaruv endpointlari."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import CredentialsException
from app.core.security import hash_password, verify_password
from app.database import get_oltp_db
from app.models.oltp.user import User, UserRole
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["Foydalanuvchilar"])


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class UpdateProfileSchema(BaseModel):
    full_name: str | None = Field(None, max_length=256)
    email: EmailStr | None = None


class LinkSchema(BaseModel):
    user_id: int
    target_id: int


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


_RESET_TOKENS: dict[str, int] = {}


@router.post("/me/change-password")
def change_password(
    payload: ChangePasswordSchema,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, user.hashed_password):
        raise CredentialsException("Eski parol noto'g'ri")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"success": True, "message": "Parol o'zgartirildi"}


@router.put("/me", response_model=UserResponse)
def update_profile(
    payload: UpdateProfileSchema,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None and payload.email != user.email:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing and existing.id != user.id:
            raise HTTPException(409, "Bu email allaqachon ishlatilgan")
        user.email = payload.email
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[UserResponse], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_oltp_db)):
    return db.query(User).all()


@router.put("/{user_id}/role", dependencies=[Depends(require_admin)])
def change_user_role(user_id: int, role: UserRole, db: Session = Depends(get_oltp_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    user.role = role
    db.commit()
    return {"success": True, "user_id": user_id, "role": role.value}


@router.put("/{user_id}/active", dependencies=[Depends(require_admin)])
def toggle_user_active(user_id: int, is_active: bool, db: Session = Depends(get_oltp_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    user.is_active = is_active
    db.commit()
    return {"success": True, "user_id": user_id, "is_active": is_active}


# ============================================================
# User-Student/Teacher real linking
# ============================================================


@router.post("/link/student", dependencies=[Depends(require_admin)])
def link_user_to_student(payload: LinkSchema, db: Session = Depends(get_oltp_db)):
    """User hisobini talaba bilan bog'lash."""
    from app.models.oltp.student import Student

    user = db.query(User).filter(User.id == payload.user_id).first()
    student = db.query(Student).filter(Student.id == payload.target_id).first()
    if not user or not student:
        raise HTTPException(404, "User yoki talaba topilmadi")
    if student.user_id and student.user_id != user.id:
        raise HTTPException(409, "Bu talaba allaqachon boshqa user bilan bog'langan")
    student.user_id = user.id
    db.commit()
    return {"success": True, "user": user.username, "student": student.full_name}


@router.post("/link/teacher", dependencies=[Depends(require_admin)])
def link_user_to_teacher(payload: LinkSchema, db: Session = Depends(get_oltp_db)):
    """User hisobini o'qituvchi bilan bog'lash."""
    from app.models.oltp.teacher import Teacher

    user = db.query(User).filter(User.id == payload.user_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == payload.target_id).first()
    if not user or not teacher:
        raise HTTPException(404)
    if teacher.user_id and teacher.user_id != user.id:
        raise HTTPException(409, "Allaqachon bog'langan")
    teacher.user_id = user.id
    db.commit()
    return {"success": True, "user": user.username, "teacher": teacher.full_name}


@router.get("/unlinked", dependencies=[Depends(require_admin)])
def list_unlinked_users(db: Session = Depends(get_oltp_db)):
    """Bog'lanmagan user va talabalar ro'yxati."""
    from app.models.oltp.student import Student
    from app.models.oltp.teacher import Teacher

    unlinked_students = db.query(Student).filter(Student.user_id == None).limit(50).all()  # noqa: E711
    unlinked_teachers = db.query(Teacher).filter(Teacher.user_id == None).limit(50).all()  # noqa: E711
    unlinked_users = (
        db.query(User)
        .filter(User.role.in_([UserRole.STUDENT, UserRole.TEACHER]))
        .all()
    )
    linked_user_ids = {
        u_id
        for u_id in (
            [s.user_id for s in db.query(Student).filter(Student.user_id != None).all()]  # noqa: E711
            + [t.user_id for t in db.query(Teacher).filter(Teacher.user_id != None).all()]  # noqa: E711
        )
    }
    free_users = [u for u in unlinked_users if u.id not in linked_user_ids]

    return {
        "unlinked_students": [
            {"id": s.id, "student_id": s.student_id, "full_name": s.full_name}
            for s in unlinked_students
        ],
        "unlinked_teachers": [
            {"id": t.id, "teacher_id": t.teacher_id, "full_name": t.full_name}
            for t in unlinked_teachers
        ],
        "free_users": [
            {"id": u.id, "username": u.username, "full_name": u.full_name, "role": u.role.value}
            for u in free_users
        ],
    }


# ============================================================
# Parol tiklash
# ============================================================


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordSchema, db: Session = Depends(get_oltp_db)):
    """Email orqali parol tiklash tokenini yuborish."""
    import secrets
    from app.services import notification_service

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        return {"success": True, "message": "Agar email mavjud bo'lsa, link yuborildi"}

    token = secrets.token_urlsafe(32)
    _RESET_TOKENS[token] = user.id

    notification_service.create_notification(
        db,
        user_id=user.id,
        title="Parolni tiklash",
        message=f"Tiklash uchun token: {token}",
        notification_type="info",
        link=f"/reset-password?token={token}",
        send_email=True,
    )

    # Dev rejimda token qaytariladi (production da olib tashlash kerak)
    return {"success": True, "message": "Email yuborildi", "_dev_token": token}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordSchema, db: Session = Depends(get_oltp_db)):
    """Token orqali parol o'zgartirish."""
    user_id = _RESET_TOKENS.get(payload.token)
    if not user_id:
        raise HTTPException(400, "Yaroqsiz yoki muddati o'tgan token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404)

    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    del _RESET_TOKENS[payload.token]
    return {"success": True, "message": "Parol o'zgartirildi"}
