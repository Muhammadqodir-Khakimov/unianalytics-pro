"""Billing endpointlari — pricing plans, subscriptions, payments."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_oltp_db
from app.models.oltp.billing import Invoice, PlanType, Subscription, SubscriptionStatus
from app.services.payment_gateways import click, payme

router = APIRouter(prefix="/billing", tags=["Billing"])


# ============================================================
# PLANS (Public)
# ============================================================


PLANS = {
    PlanType.FREE: {
        "name": "Bepul",
        "price": 0,
        "currency": "UZS",
        "students_limit": 100,
        "features": [
            "Asosiy CRUD",
            "Cheklangan dashboard",
            "Email yordam",
        ],
        "best_for": "Kichik institut, sinov uchun",
    },
    PlanType.PRO: {
        "name": "PRO",
        "price": 1_500_000,
        "currency": "UZS",
        "students_limit": 2000,
        "features": [
            "Barcha OLAP imkoniyatlar",
            "AI/ML modellar (XGBoost, K-Means, Forecast)",
            "Telegram bot",
            "Custom branding (logo, ranglar)",
            "Tezkor email yordam",
        ],
        "best_for": "O'rta universitet (100-2000 talaba)",
    },
    PlanType.ENTERPRISE: {
        "name": "Enterprise",
        "price": 9_000_000,
        "currency": "UZS",
        "students_limit": 50000,
        "features": [
            "PRO + barcha qo'shimcha",
            "HEMIS to'liq integratsiya",
            "AI Tutor (Claude/OpenAI)",
            "Mobile app (white-label)",
            "SSO va OAuth",
            "Dedicated support 24/7",
            "On-premise deployment",
            "SLA 99.9%",
        ],
        "best_for": "Yirik davlat universitetlari",
    },
    PlanType.GOVERNMENT: {
        "name": "Government",
        "price": None,
        "currency": "UZS",
        "students_limit": None,
        "features": [
            "Vazirlik darajasidagi tahlil",
            "187 universitet bir vaqtda",
            "Markaziy dashboard",
            "Custom contract",
        ],
        "best_for": "Oliy ta'lim vazirligi",
    },
}


@router.get("/plans")
def get_plans():
    """Pricing plans — public endpoint."""
    return [
        {
            "code": code.value,
            **info,
        }
        for code, info in PLANS.items()
    ]


# ============================================================
# SUBSCRIPTIONS (Admin)
# ============================================================


class SubscribeRequest(BaseModel):
    tenant_id: int
    plan: PlanType
    months: int = 12
    payment_method: str = "click"  # click / payme / bank


def _create_subscription(db: Session, tenant_id: int, plan: PlanType, months: int) -> Subscription:
    """Yangi subscription yaratish."""
    today = date.today()
    fee = float(PLANS[plan]["price"] or 0)

    sub = Subscription(
        tenant_id=tenant_id,
        plan=plan,
        status=SubscriptionStatus.TRIAL if plan == PlanType.FREE else SubscriptionStatus.ACTIVE,
        started_at=today,
        expires_at=today + timedelta(days=30 * months),
        trial_ends_at=today + timedelta(days=30) if plan != PlanType.FREE else None,
        monthly_fee=fee,
        currency="UZS",
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.post("/subscribe")
def subscribe(payload: SubscribeRequest, db: Session = Depends(get_oltp_db)):
    """Tenant uchun plan ni faollashtirish."""
    sub = _create_subscription(db, payload.tenant_id, payload.plan, payload.months)

    # Invoice yaratish
    invoice = None
    if sub.monthly_fee and sub.monthly_fee > 0:
        invoice = _create_invoice(db, sub, payload.months)

    payment_url = None
    if invoice and payload.payment_method == "click":
        payment_url = click.generate_payment_url(invoice.id, float(invoice.amount))
    elif invoice and payload.payment_method == "payme":
        payment_url = payme.generate_checkout_url(invoice.id, float(invoice.amount))

    return {
        "subscription_id": sub.id,
        "plan": sub.plan.value,
        "status": sub.status.value,
        "expires_at": sub.expires_at.isoformat(),
        "invoice_id": invoice.id if invoice else None,
        "payment_url": payment_url,
    }


def _create_invoice(db: Session, sub: Subscription, months: int) -> Invoice:
    """Subscription uchun invoice yaratish."""
    today = date.today()
    invoice_num = f"INV-{today.strftime('%Y%m%d')}-{sub.id:05d}"
    invoice = Invoice(
        subscription_id=sub.id,
        invoice_number=invoice_num,
        amount=float(sub.monthly_fee) * months,
        currency=sub.currency,
        issued_at=today,
        due_at=today + timedelta(days=14),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/subscriptions", dependencies=[Depends(require_admin)])
def list_subscriptions(db: Session = Depends(get_oltp_db)):
    items = db.query(Subscription).order_by(Subscription.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "tenant_id": s.tenant_id,
            "plan": s.plan.value,
            "status": s.status.value,
            "expires_at": s.expires_at.isoformat(),
            "monthly_fee": float(s.monthly_fee),
            "currency": s.currency,
        }
        for s in items
    ]


@router.get("/invoices", dependencies=[Depends(require_admin)])
def list_invoices(db: Session = Depends(get_oltp_db)):
    items = db.query(Invoice).order_by(Invoice.issued_at.desc()).all()
    return [
        {
            "id": i.id,
            "invoice_number": i.invoice_number,
            "amount": float(i.amount),
            "currency": i.currency,
            "issued_at": i.issued_at.isoformat(),
            "due_at": i.due_at.isoformat(),
            "paid_at": i.paid_at.isoformat() if i.paid_at else None,
            "status": i.status,
        }
        for i in items
    ]


# ============================================================
# WEBHOOKS (Click, Payme)
# ============================================================


@router.post("/webhook/click")
async def click_webhook(request: Request, db: Session = Depends(get_oltp_db)):
    """Click to'lov tasdiqlash webhook."""
    payload = await request.json() if request.headers.get("content-type", "").startswith("application/json") else dict(await request.form())
    if not click.verify_signature(payload, payload.get("sign_string", "")):
        raise HTTPException(403, "Yaroqsiz signature")

    invoice_id = int(payload.get("merchant_trans_id", 0))
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return {"error": -5, "error_note": "Invoice topilmadi"}

    if payload.get("action") == "1":  # complete
        invoice.status = "paid"
        invoice.paid_at = date.today()
        invoice.paid_amount = float(invoice.amount)
        invoice.payment_method = "click"
        invoice.transaction_id = str(payload.get("click_trans_id"))
        db.commit()

    return {"error": 0, "error_note": "Success"}


@router.post("/webhook/payme")
async def payme_webhook(request: Request, db: Session = Depends(get_oltp_db)):
    """Payme JSON-RPC webhook (qisqartirilgan)."""
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})

    if method == "PerformTransaction":
        invoice_id = int(params.get("account", {}).get("invoice_id", 0))
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            invoice.status = "paid"
            invoice.paid_at = date.today()
            invoice.payment_method = "payme"
            invoice.transaction_id = params.get("id")
            db.commit()
        return {"result": {"transaction": params.get("id"), "state": 2}}

    return {"result": {"allow": True}}
