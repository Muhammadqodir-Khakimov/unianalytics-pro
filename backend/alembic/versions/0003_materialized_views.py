"""Materialized views for dashboard speed.

Revision ID: 0003_mv
Revises: 0002_perf_idx
Create Date: 2026-05-17

Pre-aggregated dashboards. Refresh schedule: every hour via Celery beat.
- mv_faculty_gpa_monthly
- mv_subject_pass_rate
- mv_dropout_risk_summary
"""
from alembic import op

revision = "0003_mv"
down_revision = "0002_perf_idx"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Faculty x Month GPA
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_faculty_gpa_monthly AS
        SELECT
            f.faculty_id,
            f.name AS faculty_name,
            t.year,
            t.month,
            AVG(fg.grade_value) AS avg_gpa,
            COUNT(*) AS total_grades,
            COUNT(DISTINCT fg.student_key) AS unique_students
        FROM fact_grades fg
        JOIN dim_faculty f ON fg.faculty_key = f.faculty_key
        JOIN dim_time t ON fg.time_key = t.time_key
        GROUP BY f.faculty_id, f.name, t.year, t.month
    """)
    op.execute("CREATE UNIQUE INDEX ix_mv_fac_gpa_pk ON mv_faculty_gpa_monthly (faculty_id, year, month)")

    # Subject pass rate
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_subject_pass_rate AS
        SELECT
            s.subject_id,
            s.name AS subject_name,
            COUNT(*) FILTER (WHERE fg.grade_value >= 60) * 1.0 / NULLIF(COUNT(*), 0) AS pass_rate,
            COUNT(*) AS total_grades,
            AVG(fg.grade_value) AS avg_grade
        FROM fact_grades fg
        JOIN dim_subject s ON fg.subject_key = s.subject_key
        GROUP BY s.subject_id, s.name
    """)
    op.execute("CREATE UNIQUE INDEX ix_mv_subj_pass_pk ON mv_subject_pass_rate (subject_id)")

    # Dropout risk summary
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_dropout_risk_summary AS
        SELECT
            f.faculty_id,
            f.name AS faculty_name,
            ds.status,
            COUNT(*) AS student_count,
            AVG(ds.avg_gpa) AS avg_gpa
        FROM dim_student ds
        JOIN dim_faculty f ON ds.faculty_key = f.faculty_key
        WHERE ds.is_current = TRUE
        GROUP BY f.faculty_id, f.name, ds.status
    """)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_dropout_risk_summary")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_subject_pass_rate")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_faculty_gpa_monthly")
