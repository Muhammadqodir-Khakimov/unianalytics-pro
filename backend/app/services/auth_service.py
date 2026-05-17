"""Auth biznes logikasi — ro'yxatdan o'tish, login, token refresh."""
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import ConflictException, CredentialsException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.oltp.user import User
from app.schemas.auth import TokenResponse, UserRegister


def register_user(db: Session, payload: UserRegister) -> User:
    """Yangi userni ro'yxatga olish."""
    if db.query(User).filter(User.username == payload.username).first():
        raise ConflictException("Bunday username allaqachon mavjud")
    if db.query(User).filter(User.email == payload.email).first():
        raise ConflictException("Bunday email allaqachon mavjud")

    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User:
    """Login uchun userni tekshirish."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise CredentialsException("Noto'g'ri username yoki parol")
    if not user.is_active:
        raise CredentialsException("Foydalanuvchi faol emas")
    return user


def build_tokens(user: User) -> TokenResponse:
    """User uchun access + refresh tokenlarni yaratish."""
    return TokenResponse(
        access_token=create_access_token(subject=user.username, role=user.role.value),
        refresh_token=create_refresh_token(subject=user.username),
        expires_in=settings.access_token_expire_minutes * 60,
    )


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
    """Refresh token orqali yangi access token olish."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise CredentialsException("Refresh token kerak")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise CredentialsException()
    return build_tokens(user)
