"""Scheduled report tasklari."""
from loguru import logger

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.report_tasks.send_weekly_reports")
def send_weekly_reports() -> dict:
    """Har dushanba ertasi dekanlarga haftalik hisobotni email orqali yuborish."""
    from app.database import oltp_session, olap_session
    from app.models.oltp.user import User, UserRole
    from app.services import notification_service
    from app.services.report_service import build_pdf_report
    from sqlalchemy import text

    sent = 0
    with oltp_session() as oltp, olap_session() as olap:
        deans = oltp.query(User).filter(User.role == UserRole.DEKAN).all()
        for dean in deans:
            # Top faktlar olish
            rows = olap.execute(
                text(
                    """SELECT fac.faculty_name, COUNT(*) AS grades, ROUND(AVG(f.grade_value), 2) AS avg
                       FROM fact_student_grades f
                       JOIN dim_faculty fac ON f.faculty_key = fac.faculty_key
                       GROUP BY fac.faculty_name"""
                )
            ).mappings().all()
            data = [[r["faculty_name"], r["grades"], r["avg"]] for r in rows]

            try:
                pdf_bytes = build_pdf_report("Haftalik hisobot", ["Fakultet", "Baholar", "O'rtacha"], data)
                # Email yuborish
                notification_service.create_notification(
                    oltp,
                    user_id=dean.id,
                    title="Haftalik hisobot tayyor",
                    message=f"Yangi haftalik hisobot tayyorlandi ({len(data)} ta fakultet).",
                    notification_type="info",
                    link="/reports",
                    send_email=True,
                )
                sent += 1
            except Exception as e:
                logger.error("Report error for {}: {}", dean.username, e)

    return {"reports_sent": sent}
