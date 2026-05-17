"""Materialized views for dashboard speed (PostgreSQL only).

Revision ID: 0003_mv
Revises: 0002_perf_idx
Create Date: 2026-05-17

Pre-aggregated dashboards. Refresh schedule: every hour via Celery beat.
- mv_faculty_gpa_monthly
- mv_subject_pass_rate
- mv_student_gpa_summary

SQLite materialized view'ni qo'llab-quvvatlamaydi — dialect != postgresql
bo'lsa, migratsiya nop sifatida o'tadi (dev/test muhitlar buzilmasligi uchun).
"""
from alembic import op

revision = "0003_mv"
down_revision = "0002_perf_idx"
branch_labels = None
depends_on = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    if not _is_postgres():
        return  # SQLite va boshqalar — MV qo'llab-quvvatlanmaydi

    # Faculty × Year × Semester GPA
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_faculty_gpa_monthly AS
        SELECT
            f.faculty_key,
            f.faculty_name,
            t.academic_year,
            t.year,
            t.semester,
            ROUND(AVG(fg.grade_value)::numeric, 2) AS avg_grade,
            ROUND(AVG(fg.gpa_points)::numeric, 3) AS avg_gpa,
            COUNT(*)                                AS total_grades,
            COUNT(DISTINCT fg.student_key)          AS unique_students
        FROM fact_student_grades fg
        JOIN dim_faculty f ON fg.faculty_key = f.faculty_key
        JOIN dim_time t    ON fg.time_key    = t.time_key
        GROUP BY f.faculty_key, f.faculty_name, t.academic_year, t.year, t.semester
    """)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_mv_fac_gpa_pk "
        "ON mv_faculty_gpa_monthly (faculty_key, academic_year, year, semester)"
    )

    # Subject pass rate
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_subject_pass_rate AS
        SELECT
            s.subject_key,
            s.subject_code,
            s.subject_name,
            ROUND(
                COUNT(*) FILTER (WHERE fg.is_passed) * 1.0
                / NULLIF(COUNT(*), 0),
                3
            )                                AS pass_rate,
            COUNT(*)                          AS total_grades,
            ROUND(AVG(fg.grade_value)::numeric, 2) AS avg_grade
        FROM fact_student_grades fg
        JOIN dim_subject s ON fg.subject_key = s.subject_key
        GROUP BY s.subject_key, s.subject_code, s.subject_name
    """)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_mv_subj_pass_pk "
        "ON mv_subject_pass_rate (subject_key)"
    )

    # Talaba GPA xulosa (TZ — risk guruh aniqlash uchun)
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_student_gpa_summary AS
        SELECT
            ds.student_key,
            ds.student_id,
            ds.full_name,
            ds.group_name,
            ds.status,
            ROUND(AVG(fg.gpa_points)::numeric, 3)            AS avg_gpa,
            ROUND(AVG(fg.grade_value)::numeric, 2)           AS avg_grade,
            ROUND(AVG(fg.attendance_percentage)::numeric, 2) AS avg_attendance,
            COUNT(*)                                          AS grades_count,
            COUNT(*) FILTER (WHERE NOT fg.is_passed)         AS failed_count
        FROM dim_student ds
        LEFT JOIN fact_student_grades fg ON ds.student_key = fg.student_key
        GROUP BY ds.student_key, ds.student_id, ds.full_name, ds.group_name, ds.status
    """)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_mv_student_gpa_pk "
        "ON mv_student_gpa_summary (student_key)"
    )


def downgrade() -> None:
    if not _is_postgres():
        return
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_student_gpa_summary")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_subject_pass_rate")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_faculty_gpa_monthly")
