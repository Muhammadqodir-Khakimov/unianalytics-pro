"""Foydalanuvchi modeli (auth)."""
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"        # platforma egasi (SaaS)
    UNIVERSITY_ADMIN = "university_admin"  # tenant admin
    ADMIN = "admin"                    # university admin alternativ nomi
    RECTOR = "rector"                  # rektor — universitet rahbari
    DEKAN = "dekan"                    # fakultet boshlig'i
    TEACHER = "teacher"                # o'qituvchi
    STUDENT = "student"                # talaba
    MINISTRY_VIEWER = "ministry_viewer"  # vazirlik (read-only)
    PUBLIC = "public"                  # tashqi (widget uchun)


class User(OLTPBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        default=UserRole.STUDENT,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # 2FA (TOTP)
    totp_secret: Mapped[str | None] = mapped_column(String(64))
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # OAuth
    google_id: Mapped[str | None] = mapped_column(String(128), unique=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512))

    # Tenant
    tenant_id: Mapped[int | None] = mapped_column(Integer, index=True)

    # Email verification
    email_verification_token: Mapped[str | None] = mapped_column(String(128))

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"
