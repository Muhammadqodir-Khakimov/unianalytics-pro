"""FastAPI dependencies — joriy user, RBAC."""
from typing import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import CredentialsException, PermissionDeniedException
from app.core.security import decode_token
from app.database import get_oltp_db
from app.models.oltp.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_oltp_db),
) -> User:
    """JWT tokendan joriy userni qaytaradi."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise CredentialsException("Access token kerak")

    username = payload.get("sub")
    if not username:
        raise CredentialsException()

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise CredentialsException("Foydalanuvchi topilmadi")
    if not user.is_active:
        raise CredentialsException("Foydalanuvchi faol emas")
    return user


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    """RBAC: berilgan rollardan biri bo'lishi shart."""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedException(
                f"Bu amal uchun {', '.join(r.value for r in allowed_roles)} ruxsati kerak"
            )
        return current_user

    return dependency


# Tez-tez ishlatish uchun shortcutlar
require_admin = require_roles(UserRole.ADMIN)
require_dekan = require_roles(UserRole.ADMIN, UserRole.DEKAN)
require_teacher = require_roles(UserRole.ADMIN, UserRole.DEKAN, UserRole.TEACHER)
require_any = require_roles(UserRole.ADMIN, UserRole.DEKAN, UserRole.TEACHER, UserRole.STUDENT)
