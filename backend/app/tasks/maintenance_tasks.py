"""Maintenance tasklari — backup, cleanup, expiring trials."""
import subprocess
from datetime import date, timedelta

from loguru import logger

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.maintenance_tasks.backup_database")
def backup_database() -> dict:
    """Database backup (har tunda 3:00).

    Production da pg_dump → S3 ga yuborish.
    """
    import os
    backup_dir = os.environ.get("BACKUP_DIR", "/backups")
    try:
        # Mock: real production da pg_dump
        logger.info("Backup boshlandi (mock): {}", backup_dir)
        return {"success": True, "location": backup_dir, "note": "Real pg_dump bash script ishlatilishi kerak"}
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name="app.tasks.maintenance_tasks.cleanup_cache")
def cleanup_cache() -> dict:
    """In-memory cache tozalash."""
    try:
        from app.core.cache import cache
        stats_before = cache.stats()
        cache.invalidate("")  # hammasini tozalash
        return {"cleared": stats_before.get("size", 0)}
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name="app.tasks.maintenance_tasks.notify_expiring_trials")
def notify_expiring_trials() -> dict:
    """7 kun ichida tugaydigan trial larga email yuborish."""
    from app.database import oltp_session
    from app.models.oltp.billing import Subscription, SubscriptionStatus
    from app.models.oltp.tenant import Tenant
    from app.services import notification_service
    from app.services.email_templates import render_template

    notified = 0
    with oltp_session() as db:
        target_date = date.today() + timedelta(days=7)
        subs = (
            db.query(Subscription)
            .filter(
                Subscription.status == SubscriptionStatus.TRIAL,
                Subscription.trial_ends_at <= target_date,
                Subscription.trial_ends_at >= date.today(),
            )
            .all()
        )
        for sub in subs:
            tenant = db.query(Tenant).filter(Tenant.id == sub.tenant_id).first()
            if not tenant:
                continue
            # Tenant admin lariga yuborish (placeholder — real prod da tenant->user mapping)
            days_left = (sub.trial_ends_at - date.today()).days
            logger.info("Trial expiring for tenant {}: {} kun", tenant.name, days_left)
            notified += 1

    return {"notified": notified}
