"""ETL boshqaruv endpointlari."""
from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import require_admin
from app.tasks.etl_tasks import run_full_etl

router = APIRouter(prefix="/etl", tags=["ETL"], dependencies=[Depends(require_admin)])


@router.post("/run")
def run_etl():
    """OLTP -> OLAP to'liq ETL ni Celery orqali ishga tushirish."""
    task = run_full_etl.delay()
    return {"task_id": task.id, "status": "queued"}


@router.get("/status/{task_id}")
def etl_status(task_id: str):
    """Celery task statusini olish."""
    from app.tasks.celery_app import celery_app

    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    if task.state == "FAILURE":
        raise HTTPException(status_code=500, detail=str(task.result))
    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.ready() else None,
    }
