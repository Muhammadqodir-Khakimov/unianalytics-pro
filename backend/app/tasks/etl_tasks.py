"""Celery tasklari — ETL va periodik vazifalar."""
from app.services import etl_service
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.etl_tasks.run_full_etl", bind=True)
def run_full_etl(self):
    """OLTP -> OLAP to'liq ETL."""
    return etl_service.run_full_etl()


@celery_app.task(name="app.tasks.etl_tasks.refresh_materialized_views")
def refresh_materialized_views():
    """Materialized view larni yangilash."""
    etl_service.refresh_materialized_views()
    return {"status": "ok"}
