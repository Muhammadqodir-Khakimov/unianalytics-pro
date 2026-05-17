"""Hisobot endpointlari."""
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import require_dekan
from app.database import get_olap_db
from app.olap.cube import get_cube
from app.olap.query_builder import FilterClause, OLAPQuery, OLAPQueryBuilder
from app.schemas.olap import OLAPQuerySchema
from app.services.report_service import build_excel_report, build_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"], dependencies=[Depends(require_dekan)])


class ReportRequest(BaseModel):
    title: str = "Hisobot"
    format: Literal["pdf", "excel"] = "excel"
    query: OLAPQuerySchema


class GenerateRequest(BaseModel):
    title: str = "Hisobot"
    query: OLAPQuerySchema


def _execute_to_rows(payload: OLAPQuerySchema, db: Session):
    cube = get_cube(payload.cube_name)
    query = OLAPQuery(
        cube_name=payload.cube_name,
        dimensions=[d.model_dump() for d in payload.dimensions],
        measures=payload.measures,
        filters=[FilterClause(**f.model_dump()) for f in payload.filters],
        order_by=payload.order_by,
        limit=payload.limit,
        grouping_mode=payload.grouping_mode,
    )
    return OLAPQueryBuilder(cube).execute(db, query)


def _pdf_response(title: str, rows: list[dict]) -> Response:
    headers = list(rows[0].keys()) if rows else []
    data = [[row.get(h) for h in headers] for row in rows]
    content = build_pdf_report(title, headers, data)
    return Response(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{title}.pdf"'},
    )


def _excel_response(title: str, rows: list[dict]) -> Response:
    headers = list(rows[0].keys()) if rows else []
    data = [[row.get(h) for h in headers] for row in rows]
    content = build_excel_report(title, headers, data)
    return Response(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{title}.xlsx"'},
    )


def _get_templates() -> list[dict]:
    return [
        {
            "name": "faculty_performance",
            "title": "Fakultetlar bo'yicha o'zlashtirish",
            "description": "Har bir fakultet uchun o'rtacha ball, GPA va o'tish darajasi",
            "query": {
                "dimensions": [{"dimension": "faculty", "attribute": "faculty_name"}],
                "measures": ["avg_grade", "avg_gpa", "total_grades", "passed_count"],
            },
        },
        {
            "name": "yearly_trend",
            "title": "Yillik dinamika",
            "description": "Har semester va o'quv yili bo'yicha o'rtacha ko'rsatkichlar",
            "query": {
                "dimensions": [
                    {"dimension": "time", "attribute": "academic_year"},
                    {"dimension": "time", "attribute": "semester"},
                ],
                "measures": ["avg_grade", "avg_gpa"],
            },
        },
        {
            "name": "top_students",
            "title": "Eng yaxshi talabalar",
            "description": "GPA bo'yicha eng yaxshi talabalar ro'yxati",
            "query": {
                "dimensions": [
                    {"dimension": "student", "attribute": "student_id"},
                    {"dimension": "student", "attribute": "full_name"},
                ],
                "measures": ["avg_gpa", "avg_grade", "total_grades"],
                "order_by": ["avg_gpa DESC"],
                "limit": 100,
            },
        },
    ]


@router.post("/generate")
def generate_report(payload: ReportRequest, db: Session = Depends(get_olap_db)):
    """OLAP query asosida PDF yoki Excel hisobot (format payload da)."""
    rows = _execute_to_rows(payload.query, db)
    if payload.format == "pdf":
        return _pdf_response(payload.title, rows)
    return _excel_response(payload.title, rows)


@router.post("/generate/pdf")
def generate_pdf(payload: GenerateRequest, db: Session = Depends(get_olap_db)):
    """PDF hisobot generatsiyasi (prompt talabi)."""
    rows = _execute_to_rows(payload.query, db)
    return _pdf_response(payload.title, rows)


@router.post("/generate/excel")
def generate_excel(payload: GenerateRequest, db: Session = Depends(get_olap_db)):
    """Excel hisobot generatsiyasi (prompt talabi)."""
    rows = _execute_to_rows(payload.query, db)
    return _excel_response(payload.title, rows)


@router.get("/list")
def list_reports():
    """Tayyor hisobot shablonlari (prompt talabi)."""
    return _get_templates()


@router.get("/templates")
def list_templates():
    """Tayyor hisobot shablonlari (alias)."""
    return _get_templates()
