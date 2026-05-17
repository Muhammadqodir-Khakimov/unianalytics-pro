"""Multi-tenancy va white-labeling endpointlari."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_oltp_db
from app.models.oltp.tenant import Tenant

router = APIRouter(prefix="/tenants", tags=["Multi-tenancy"])


class TenantCreate(BaseModel):
    code: str
    name: str
    short_name: str
    domain: str | None = None
    primary_color: str = "#1677ff"
    secondary_color: str = "#722ed1"
    logo_url: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    description: str | None = None
    max_students: int = 10_000


class TenantUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    logo_url: str | None = None
    favicon_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    description: str | None = None
    is_active: bool | None = None
    max_students: int | None = None


def _to_dict(t: Tenant) -> dict:
    return {
        "id": t.id,
        "code": t.code,
        "name": t.name,
        "short_name": t.short_name,
        "domain": t.domain,
        "logo_url": t.logo_url,
        "favicon_url": t.favicon_url,
        "primary_color": t.primary_color,
        "secondary_color": t.secondary_color,
        "address": t.address,
        "phone": t.phone,
        "email": t.email,
        "website": t.website,
        "description": t.description,
        "is_active": t.is_active,
        "max_students": t.max_students,
        "license_until": t.license_until.isoformat() if t.license_until else None,
    }


@router.get("/current")
def current_tenant(db: Session = Depends(get_oltp_db)):
    """Joriy tenant — host yoki birinchi mavjud bo'lgan.

    Real production da request.url.hostname dan aniqlash kerak.
    Hozir esa birinchi mavjud bo'lganni qaytaramiz (single-tenant mode default).
    """
    t = db.query(Tenant).filter(Tenant.is_active == True).first()  # noqa: E712
    if not t:
        # Default tenant qaytarish
        return {
            "id": 0,
            "code": "default",
            "name": "Toshkent Davlat Universiteti",
            "short_name": "TDU",
            "primary_color": "#1677ff",
            "secondary_color": "#722ed1",
            "logo_url": None,
            "address": "Toshkent shahar",
            "phone": "+998 71 246 02 24",
            "email": "info@tdu.uz",
            "website": "https://tdu.uz",
        }
    return _to_dict(t)


@router.get("", dependencies=[Depends(require_admin)])
def list_tenants(db: Session = Depends(get_oltp_db)):
    return [_to_dict(t) for t in db.query(Tenant).all()]


@router.post("", dependencies=[Depends(require_admin)])
def create_tenant(payload: TenantCreate, db: Session = Depends(get_oltp_db)):
    existing = db.query(Tenant).filter(Tenant.code == payload.code).first()
    if existing:
        raise HTTPException(409, "Bunday kod allaqachon mavjud")
    t = Tenant(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return _to_dict(t)


@router.put("/{tenant_id}", dependencies=[Depends(require_admin)])
def update_tenant(tenant_id: int, payload: TenantUpdate, db: Session = Depends(get_oltp_db)):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(404)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return _to_dict(t)


@router.get("/branding/current")
def public_branding(db: Session = Depends(get_oltp_db)):
    """Public endpoint — frontend uchun brand ma'lumotlari (login sahifa)."""
    t = db.query(Tenant).filter(Tenant.is_active == True).first()  # noqa: E712
    if not t:
        return {
            "name": "Student Rating OLAP",
            "short_name": "SR",
            "logo_url": None,
            "primary_color": "#1677ff",
        }
    return {
        "name": t.name,
        "short_name": t.short_name,
        "logo_url": t.logo_url,
        "favicon_url": t.favicon_url,
        "primary_color": t.primary_color,
        "secondary_color": t.secondary_color,
    }
