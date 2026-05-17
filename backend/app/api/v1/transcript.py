"""Talaba akademik transkripti — rasmiy hujjat sifatida PDF."""
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import require_any
from app.database import get_olap_db, get_oltp_db
from app.models.oltp.student import Student

router = APIRouter(prefix="/transcript", tags=["Transkript"], dependencies=[Depends(require_any)])


@router.get("/student/{student_id}")
def student_transcript(
    student_id: int,
    oltp: Session = Depends(get_oltp_db),
    olap: Session = Depends(get_olap_db),
):
    """Talaba uchun rasmiy akademik transkript PDF."""
    student = oltp.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Talaba topilmadi")

    # Barcha baholarni semesterga ko'ra olamiz
    rows = olap.execute(
        text(
            """
            SELECT t.academic_year, t.semester,
                   s.subject_name, s.subject_code, s.credit_hours,
                   ROUND(AVG(f.grade_value), 2) AS final_grade,
                   ROUND(AVG(f.gpa_points), 2) AS gpa_points,
                   MIN(CASE WHEN f.is_passed THEN 'O''tdi' ELSE 'O''tmadi' END) AS status
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            JOIN dim_subject s ON f.subject_key = s.subject_key
            JOIN dim_time t ON f.time_key = t.time_key
            WHERE ds.student_id = :sid
            GROUP BY t.academic_year, t.semester, s.subject_name, s.subject_code, s.credit_hours
            ORDER BY t.academic_year, t.semester, s.subject_name
            """
        ),
        {"sid": student.student_id},
    ).mappings().all()

    overall = olap.execute(
        text(
            """
            SELECT ROUND(AVG(gpa_points), 3) AS overall_gpa,
                   ROUND(AVG(grade_value), 2) AS overall_grade,
                   SUM(credit_hours) AS total_credits
            FROM fact_student_grades f
            JOIN dim_student ds ON f.student_key = ds.student_key
            WHERE ds.student_id = :sid
            """
        ),
        {"sid": student.student_id},
    ).mappings().first() or {}

    # PDF yaratish
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=30, bottomMargin=30, leftMargin=30, rightMargin=30)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.HexColor("#1677FF"),
        spaceAfter=20,
        alignment=1,
    )

    elements = []
    elements.append(Paragraph("AKADEMIK TRANSKRIPT", title_style))
    elements.append(Paragraph(f"<b>Universitet:</b> Toshkent Davlat Universiteti", styles["Normal"]))
    elements.append(Spacer(1, 6))

    info_table = Table(
        [
            ["Talaba ID:", student.student_id, "F.I.Sh.:", student.full_name],
            [
                "Guruh:",
                student.group.name if student.group else "-",
                "Kurs:",
                str(student.group.course) if student.group else "-",
            ],
            [
                "Yo'nalish:",
                student.group.specialty.name if student.group else "-",
                "Fakultet:",
                student.group.specialty.faculty.name if student.group else "-",
            ],
            ["Kirgan yili:", str(student.enrollment_year), "Status:", student.status.value],
        ],
        colWidths=[80, 180, 80, 180],
    )
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(info_table)
    elements.append(Spacer(1, 16))

    # Semesterlar bo'yicha guruhlash
    current_period = None
    table_data: list[list[str]] = []
    for r in rows:
        period = f"{r['academic_year']} {r['semester']} semestr"
        if period != current_period:
            if table_data:
                _render_table(elements, table_data)
                elements.append(Spacer(1, 12))
                table_data = []
            elements.append(Paragraph(f"<b>{period}</b>", styles["Heading3"]))
            current_period = period
            table_data.append(["Fan kodi", "Fan nomi", "Kredit", "Ball", "GPA", "Status"])

        table_data.append([
            r["subject_code"],
            r["subject_name"],
            str(r["credit_hours"]),
            f"{float(r['final_grade']):.2f}",
            f"{float(r['gpa_points']):.2f}",
            r["status"],
        ])

    if table_data:
        _render_table(elements, table_data)

    elements.append(Spacer(1, 20))

    # Umumiy ko'rsatkichlar
    summary_table = Table(
        [
            ["UMUMIY KO'RSATKICHLAR", ""],
            ["O'rtacha ball:", f"{float(overall.get('overall_grade', 0) or 0):.2f}"],
            ["O'rtacha GPA:", f"{float(overall.get('overall_gpa', 0) or 0):.3f}"],
            ["Jami kreditlar:", str(int(overall.get("total_credits", 0) or 0))],
        ],
        colWidths=[200, 200],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1677FF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(summary_table)

    elements.append(Spacer(1, 30))
    elements.append(
        Paragraph(
            f"Hujjat yaratilgan: {datetime.now():%Y-%m-%d %H:%M}",
            ParagraphStyle("footer", parent=styles["Normal"], fontSize=9, textColor=colors.grey),
        )
    )

    doc.build(elements)

    return Response(
        buf.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="transcript_{student.student_id}.pdf"'
        },
    )


def _render_table(elements: list, data: list[list[str]]):
    table = Table(data, colWidths=[60, 220, 50, 50, 50, 60])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6F4FF")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(table)
