"""Celery ilovasi konfiguratsiyasi."""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "student_rating_olap",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.etl_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tashkent",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)

celery_app.conf.beat_schedule = {
    "etl-hourly": {
        "task": "app.tasks.etl_tasks.run_full_etl",
        "schedule": crontab(minute=0),  # har soatda
    },
    "refresh-materialized-views-nightly": {
        "task": "app.tasks.etl_tasks.refresh_materialized_views",
        "schedule": crontab(minute=0, hour=2),  # tunda soat 2 da
    },
}
