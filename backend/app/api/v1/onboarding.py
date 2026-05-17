"""Onboarding wizard — yangi universitet uchun setup."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database import get_oltp_db
from app.models.oltp.billing import PlanType, Subscription, SubscriptionStatus
from app.models.oltp.tenant import Tenant
from app.models.oltp.user import User, UserRole

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


class OnboardingStart(BaseModel):
    """Step 1: Universitet va admin user yaratish."""
    university_name: str
    university_code: str
    short_name: str
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    phone: str | None = None
    address: str | None = None
    estimated_students: int = 1000


class BrandingPayload(BaseModel):
    """Step 2: Branding."""
    tenant_id: int
    primary_color: str = "#1677ff"
    secondary_color: str = "#722ed1"
    logo_url: str | None = None


class PlanChoice(BaseModel):
    """Step 3: Plan tanlash."""
    tenant_id: int
    plan: PlanType = PlanType.FREE


@router.post("/start")
def onboarding_start(payload: OnboardingStart, db: Session = Depends(get_oltp_db)):
    """Yangi tashkilot uchun setup boshlash."""
    # Tenant code unikalligini tekshirish
    existing = db.query(Tenant).filter(Tenant.code == payload.university_code).first()
    if existing:
        raise HTTPException(409, "Bunday kod allaqachon mavjud")

    # 1. Tenant
    tenant = Tenant(
        code=payload.university_code,
        name=payload.university_name,
        short_name=payload.short_name,
        phone=payload.phone,
        address=payload.address,
        email=payload.admin_email,
        max_students=payload.estimated_students,
    )
    db.add(tenant)
    db.flush()

    # 2. Admin user
    admin_username = f"admin_{payload.university_code.lower()}"
    if db.query(User).filter(User.username == admin_username).first():
        admin_username = f"admin_{payload.university_code.lower()}_{tenant.id}"

    admin = User(
        username=admin_username,
        email=payload.admin_email,
        full_name=payload.admin_name,
        hashed_password=hash_password(payload.admin_password),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=False,
    )
    db.add(admin)
    db.commit()

    return {
        "tenant_id": tenant.id,
        "admin_user_id": admin.id,
        "admin_username": admin_username,
        "next_step": "branding",
        "message": f"Tashkilot yaratildi: {tenant.name}. Endi brand sozlash.",
    }


@router.post("/branding")
def onboarding_branding(payload: BrandingPayload, db: Session = Depends(get_oltp_db)):
    """Logo, ranglar."""
    tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
    if not tenant:
        raise HTTPException(404)

    tenant.primary_color = payload.primary_color
    tenant.secondary_color = payload.secondary_color
    if payload.logo_url:
        tenant.logo_url = payload.logo_url
    db.commit()

    return {"tenant_id": tenant.id, "next_step": "choose_plan"}


@router.post("/choose-plan")
def onboarding_plan(payload: PlanChoice, db: Session = Depends(get_oltp_db)):
    """Plan tanlash va 30 kunlik trial."""
    tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
    if not tenant:
        raise HTTPException(404)

    # Trial — 30 kun bepul
    sub = Subscription(
        tenant_id=tenant.id,
        plan=payload.plan,
        status=SubscriptionStatus.TRIAL,
        started_at=date.today(),
        expires_at=date.today() + timedelta(days=30),
        trial_ends_at=date.today() + timedelta(days=30),
        monthly_fee=0,
    )
    db.add(sub)
    db.commit()

    return {
        "tenant_id": tenant.id,
        "subscription_id": sub.id,
        "trial_ends_at": sub.trial_ends_at.isoformat(),
        "next_step": "complete",
        "message": "30 kunlik bepul sinov boshlandi!",
    }


@router.post("/complete/{tenant_id}")
def onboarding_complete(tenant_id: int, db: Session = Depends(get_oltp_db)):
    """Setup tugatish — sample data yuklash va welcome xabarini yuborish."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404)

    return {
        "tenant_id": tenant.id,
        "status": "ready",
        "login_url": f"https://{tenant.code}.unianalytics.uz",
        "credentials_hint": "Email orqali login qiling",
        "next_actions": [
            "Talabalar ro'yxatini Excel orqali yuklang",
            "O'qituvchilar ro'yxati",
            "Fanlar va guruhlar",
            "HEMIS integratsiya sozlash (Enterprise plan)",
        ],
    }


@router.get("/steps")
def onboarding_steps():
    """Onboarding bosqichlari frontend uchun."""
    return [
        {"id": 1, "code": "start", "title": "Tashkilot ma'lumotlari", "description": "Nom, admin user"},
        {"id": 2, "code": "branding", "title": "Brand", "description": "Logo, ranglar"},
        {"id": 3, "code": "plan", "title": "Plan tanlash", "description": "Free / Pro / Enterprise"},
        {"id": 4, "code": "complete", "title": "Tayyor", "description": "Tizimga kirish"},
    ]
