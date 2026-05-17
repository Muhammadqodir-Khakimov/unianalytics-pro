"""Multi-tenancy model — har bir tashkilot (universitet) uchun ajratilgan brendlik."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


class Tenant(OLTPBase):
    """Universitet/tashkilot. Bir necha universitet bitta tizimda ishlay oladi."""

    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # masalan: tdu, tatu
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    short_name: Mapped[str] = mapped_column(String(64))
    domain: Mapped[str | None] = mapped_column(String(128), unique=True)  # tdu.olap.uz

    # Branding
    logo_url: Mapped[str | None] = mapped_column(String(512))
    favicon_url: Mapped[str | None] = mapped_column(String(512))
    primary_color: Mapped[str] = mapped_column(String(16), default="#1677ff")
    secondary_color: Mapped[str] = mapped_column(String(16), default="#722ed1")

    # Kontakt
    address: Mapped[str | None] = mapped_column(String(512))
    phone: Mapped[str | None] = mapped_column(String(64))
    email: Mapped[str | None] = mapped_column(String(128))
    website: Mapped[str | None] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    license_until: Mapped[datetime | None] = mapped_column(DateTime)
    max_students: Mapped[int] = mapped_column(default=10_000)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Permission(OLTPBase):
    """Granular permission — har bir resurs uchun aniq ruxsat."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(256))
    category: Mapped[str] = mapped_column(String(32), index=True)  # student/grade/report/admin


class RolePermission(OLTPBase):
    """Rol ↔ Permission bog'lanish."""

    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(32), index=True)
    permission_id: Mapped[int] = mapped_column(index=True)
    granted: Mapped[bool] = mapped_column(Boolean, default=True)


class Webhook(OLTPBase):
    """Tashqi tizimlarga event yuborish uchun webhook konfiguratsiyasi."""

    __tablename__ = "webhooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    secret: Mapped[str | None] = mapped_column(String(128))  # HMAC uchun
    events: Mapped[str] = mapped_column(String(512))  # vergul ajratilgan: grade.created,application.approved
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failure_count: Mapped[int] = mapped_column(default=0)
    last_called_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
