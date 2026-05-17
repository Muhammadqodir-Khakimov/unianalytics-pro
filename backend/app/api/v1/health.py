"""Advanced health checks va monitoring endpointlari."""
import time
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_olap_db, get_oltp_db
from app.integrations.eskiz_sms import eskiz
from app.integrations.hemis_client import hemis
from app.integrations.moodle_client import moodle

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/detailed")
def detailed_health(
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    """To'liq tizim salomatligi (DB, Redis, ML, integratsiyalar)."""
    checks: dict = {}

    # OLTP DB
    t0 = time.time()
    try:
        oltp.execute(text("SELECT 1"))
        checks["oltp_db"] = {"status": "healthy", "latency_ms": round((time.time() - t0) * 1000, 2)}
    except Exception as e:
        checks["oltp_db"] = {"status": "unhealthy", "error": str(e)}

    # OLAP DB
    t0 = time.time()
    try:
        count = olap.execute(text("SELECT COUNT(*) FROM fact_student_grades")).scalar()
        checks["olap_db"] = {
            "status": "healthy",
            "latency_ms": round((time.time() - t0) * 1000, 2),
            "fact_rows": count,
        }
    except Exception as e:
        checks["olap_db"] = {"status": "unhealthy", "error": str(e)}

    # Redis (oddiy)
    try:
        import redis
        from app.config import settings
        r = redis.Redis(host=settings.redis_host, port=settings.redis_port, socket_connect_timeout=2)
        r.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unavailable", "error": str(e)[:100]}

    # ML modellari
    ml_dir = Path(__file__).resolve().parents[3] / "ml_models"
    checks["ml_models"] = {
        "xgb_dropout": (ml_dir / "dropout_xgb.joblib").exists(),
        "kmeans_clusters": (ml_dir / "student_kmeans.joblib").exists(),
        "shap_explainer": (ml_dir / "dropout_shap.joblib").exists(),
    }

    # Integratsiyalar
    checks["integrations"] = {
        "hemis": {"configured": hemis.is_configured()},
        "moodle": {"configured": moodle.is_configured()},
        "eskiz_sms": {"configured": eskiz.is_configured()},
    }

    # Cache
    try:
        from app.core.cache import cache
        checks["cache"] = cache.stats()
    except Exception:
        checks["cache"] = {"status": "n/a"}

    # AI keys
    import os
    checks["ai_keys"] = {
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "telegram_bot": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
        "sentry": bool(os.environ.get("SENTRY_DSN")),
    }

    # Overall
    healthy = all(
        c.get("status") in ("healthy", None) or c.get("status") == "unavailable"
        for c in [checks["oltp_db"], checks["olap_db"]]
    )
    checks["overall"] = {"status": "healthy" if healthy else "degraded", "timestamp": datetime.utcnow().isoformat()}

    return checks


@router.get("/stats", dependencies=[Depends(require_admin)])
def system_stats(oltp: Session = Depends(get_oltp_db), olap: Session = Depends(get_olap_db)):
    """Tizim sttatistikasi: foydalanuvchilar, ma'lumotlar, faollik."""
    from app.models.oltp.audit import AuditLog
    from app.models.oltp.notification import Notification
    from app.models.oltp.student import Student
    from app.models.oltp.user import User
    from app.models.oltp.tenant import Tenant

    total_users = oltp.query(User).count()
    active_users = oltp.query(User).filter(User.is_active == True).count()  # noqa: E712

    recent_logs = (
        oltp.query(AuditLog)
        .filter(AuditLog.created_at >= datetime.utcnow() - timedelta(days=7))
        .count()
    )

    return {
        "users": {"total": total_users, "active": active_users},
        "students": oltp.query(Student).count(),
        "tenants": oltp.query(Tenant).count(),
        "notifications_pending": oltp.query(Notification).filter(Notification.is_read == False).count(),  # noqa: E712
        "audit_logs_last_7_days": recent_logs,
        "olap_fact_count": olap.execute(text("SELECT COUNT(*) FROM fact_student_grades")).scalar(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/saas-overview", dependencies=[Depends(require_admin)])
def saas_overview(db: Session = Depends(get_oltp_db)):
    """SaaS Super-Admin dashboard ma'lumotlari — barcha tenant lar."""
    from app.models.oltp.billing import Invoice, Subscription, SubscriptionStatus
    from app.models.oltp.tenant import Tenant

    tenants = db.query(Tenant).all()
    subs = db.query(Subscription).all()
    invoices = db.query(Invoice).all()

    total_revenue = sum(float(i.paid_amount or 0) for i in invoices if i.status == "paid")
    total_pending = sum(float(i.amount or 0) for i in invoices if i.status == "pending")

    return {
        "tenants": {
            "total": len(tenants),
            "active": sum(1 for t in tenants if t.is_active),
            "list": [
                {
                    "id": t.id,
                    "code": t.code,
                    "name": t.name,
                    "is_active": t.is_active,
                    "max_students": t.max_students,
                    "created_at": t.created_at.isoformat(),
                }
                for t in tenants
            ],
        },
        "subscriptions": {
            "total": len(subs),
            "active": sum(1 for s in subs if s.status == SubscriptionStatus.ACTIVE),
            "trial": sum(1 for s in subs if s.status == SubscriptionStatus.TRIAL),
            "by_plan": {
                p: sum(1 for s in subs if s.plan.value == p)
                for p in ["free", "pro", "enterprise", "government"]
            },
        },
        "revenue": {
            "total_collected": total_revenue,
            "pending": total_pending,
            "monthly_recurring": sum(float(s.monthly_fee or 0) for s in subs if s.status == SubscriptionStatus.ACTIVE),
        },
        "invoices": {
            "total": len(invoices),
            "paid": sum(1 for i in invoices if i.status == "paid"),
            "pending": sum(1 for i in invoices if i.status == "pending"),
            "overdue": sum(1 for i in invoices if i.status == "overdue"),
        },
    }
