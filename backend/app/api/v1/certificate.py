"""Akademik ma'lumotnoma PDF (rasmiy hujjat)."""
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from app.core.dependencies import require_any
from app.database import get_oltp_db
from app.models.oltp.student import Student

router = APIRouter(prefix="/certificate", tags=["Ma'lumotnoma"], dependencies=[Depends(require_any)])


@router.get("/student/{student_id}")
def academic_certificate(student_id: int, db: Session = Depends(get_oltp_db)):
    """Talaba uchun rasmiy akademik ma'lumotnoma."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=40, bottomMargin=40, leftMargin=50, rightMargin=50)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph(
        "<b>TOSHKENT DAVLAT UNIVERSITETI</b>",
        ParagraphStyle("h1", parent=styles["Title"], fontSize=14, alignment=1, textColor=colors.HexColor("#1677FF"))
    ))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        f"<b>{student.group.specialty.faculty.name.upper() if student.group else ''} FAKULTETI</b>",
        ParagraphStyle("h2", parent=styles["Normal"], fontSize=11, alignment=1)
    ))
    elements.append(Spacer(1, 24))

    # Title
    elements.append(Paragraph(
        "<b>MA'LUMOTNOMA</b>",
        ParagraphStyle("title", parent=styles["Title"], fontSize=20, alignment=1, spaceAfter=20)
    ))

    # Body
    body_style = ParagraphStyle(
        "body", parent=styles["Normal"], fontSize=12, leading=18, alignment=4
    )

    elements.append(Paragraph(
        f"Ushbu ma'lumotnoma <b>{student.full_name}</b>ga uning haqiqatan ham "
        f"{student.group.specialty.faculty.name if student.group else '-'} fakultetining "
        f"{student.group.specialty.name if student.group else '-'} yo'nalishi "
        f"<b>{student.group.course if student.group else '-'}-kurs</b> "
        f"<b>{student.group.name if student.group else '-'}</b> guruhi talabasi ekanligini "
        f"tasdiqlash uchun berildi.",
        body_style,
    ))
    elements.append(Spacer(1, 20))

    info = [
        ["Talaba ID:", student.student_id],
        ["F.I.Sh.:", student.full_name],
        ["Tug'ilgan sana:", student.birth_date.strftime("%d.%m.%Y") if student.birth_date else "-"],
        ["Ta'lim shakli:", student.education_form.value],
        ["Kirgan yili:", str(student.enrollment_year)],
        ["Holati:", student.status.value],
    ]
    info_table = Table(info, colWidths=[150, 350])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 32))

    # Maqsad
    elements.append(Paragraph(
        "Ma'lumotnoma talab qilingan joyga taqdim etish uchun berildi.",
        body_style,
    ))
    elements.append(Spacer(1, 60))

    # Imzo
    sig = Table(
        [
            ["Fakultet dekani:", "_" * 30, "(F.I.Sh.)"],
            ["", "(imzo, M.O'.)", ""],
            ["", "", ""],
            ["Sana:", datetime.now().strftime("%d.%m.%Y"), ""],
        ],
        colWidths=[120, 200, 150],
    )
    sig.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(sig)
    elements.append(Spacer(1, 30))

    elements.append(Paragraph(
        f"Hujjat raqami: SR-{student.id:05d}-{datetime.now():%Y%m%d}",
        ParagraphStyle("ref", parent=styles["Normal"], fontSize=9, textColor=colors.grey),
    ))

    doc.build(elements)
    return Response(
        buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="certificate_{student.student_id}.pdf"'},
    )
