"""Integration endpointlari — HEMIS, Moodle, Eskiz."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_oltp_db
from app.integrations import hemis_client, moodle_client
from app.integrations.eskiz_sms import eskiz

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/status", dependencies=[Depends(require_admin)])
def integrations_status():
    """Barcha integratsiyalar konfiguratsiya holati."""
    return {
        "hemis": {
            "configured": hemis_client.hemis.is_configured(),
            "base_url": hemis_client.hemis.base_url,
        },
        "moodle": {
            "configured": moodle_client.moodle.is_configured(),
            "base_url": moodle_client.moodle.base_url,
        },
        "eskiz_sms": {
            "configured": eskiz.is_configured(),
            "sender": eskiz.sender,
        },
    }


@router.post("/hemis/sync", dependencies=[Depends(require_admin)])
def hemis_sync(db: Session = Depends(get_oltp_db)):
    return hemis_client.sync_to_local(db)


@router.get("/hemis/students", dependencies=[Depends(require_admin)])
def hemis_students(limit: int = 20):
    return hemis_client.hemis.get_students(limit=limit)


@router.get("/moodle/courses", dependencies=[Depends(require_admin)])
def moodle_courses():
    return moodle_client.moodle.get_courses()


class SmsPayload(BaseModel):
    phone: str
    message: str


@router.post("/sms/send", dependencies=[Depends(require_admin)])
def send_sms(payload: SmsPayload):
    return eskiz.send_sms(payload.phone, payload.message)


@router.get("/sms/balance", dependencies=[Depends(require_admin)])
def sms_balance():
    bal = eskiz.get_balance()
    return {"configured": eskiz.is_configured(), "balance": bal}
