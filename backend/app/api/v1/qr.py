"""QR code talaba ID kartasi uchun."""
import base64
import io

import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.dependencies import require_any
from app.database import get_oltp_db
from app.models.oltp.student import Student

router = APIRouter(prefix="/qr", tags=["QR codes"], dependencies=[Depends(require_any)])


@router.get("/student/{student_id}")
def student_qr(student_id: int, db: Session = Depends(get_oltp_db)):
    """Talaba uchun QR code (PNG)."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)

    qr_data = f"https://unianalytics.uz/students/{student.student_id}|name={student.full_name}|group={student.group.name if student.group else '-'}"

    qr = qrcode.QRCode(version=1, box_size=10, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1677ff", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png")


@router.get("/student/{student_id}/base64")
def student_qr_base64(student_id: int, db: Session = Depends(get_oltp_db)):
    """Talaba uchun QR code base64 (frontend ga embed)."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)
    qr_data = f"https://unianalytics.uz/students/{student.student_id}"
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return {
        "student_id": student.student_id,
        "qr_data": qr_data,
        "qr_image": f"data:image/png;base64,{b64}",
    }
