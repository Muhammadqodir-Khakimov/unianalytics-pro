"""Billing va Subscription modellari."""
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"


class SubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Subscription(OLTPBase):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    plan: Mapped[PlanType] = mapped_column(SAEnum(PlanType, name="plan_type"), default=PlanType.FREE)
    status: Mapped[SubscriptionStatus] = mapped_column(
        SAEnum(SubscriptionStatus, name="sub_status"),
        default=SubscriptionStatus.TRIAL,
        index=True,
    )

    started_at: Mapped[date] = mapped_column(Date, default=date.today)
    expires_at: Mapped[date] = mapped_column(Date, nullable=False)
    trial_ends_at: Mapped[date | None] = mapped_column(Date)

    monthly_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(8), default="USD")

    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Invoice(OLTPBase):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"), index=True)
    invoice_number: Mapped[str] = mapped_column(String(32), unique=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(8), default="USD")

    issued_at: Mapped[date] = mapped_column(Date, default=date.today)
    due_at: Mapped[date] = mapped_column(Date)
    paid_at: Mapped[date | None] = mapped_column(Date)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/paid/overdue
    payment_method: Mapped[str | None] = mapped_column(String(32))  # click/payme/stripe
    transaction_id: Mapped[str | None] = mapped_column(String(128))

    pdf_url: Mapped[str | None] = mapped_column(String(512))
    notes: Mapped[str | None] = mapped_column(Text)
