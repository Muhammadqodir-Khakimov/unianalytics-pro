"""HEMIS sinxronizatsiya tasklari."""
from loguru import logger

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.hemis_tasks.sync_from_hemis")
def sync_from_hemis() -> dict:
    """HEMIS dan ma'lumotlarni olib local DB ga yangilash (har 2 soatda)."""
    from app.database import oltp_session
    from app.integrations.hemis_client import sync_to_local

    try:
        with oltp_session() as db:
            stats = sync_to_local(db)
        logger.info("HEMIS sync: {}", stats)
        return stats
    except Exception as e:
        logger.error("HEMIS sync error: {}", e)
        return {"error": str(e)}
