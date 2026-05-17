"""Performance indekslari OLAP fact + dimension jadvallari uchun.

Revision ID: 0002_perf_idx
Revises: 0001_olap_init
Create Date: 2026-05-17

Add composite indexes for the most common slice/dice queries:
- fact_grades (time_key, student_key)         — talaba progressi vaqt bo'yicha
- fact_grades (faculty_key, time_key)         — fakultet GPA trend
- fact_grades (subject_key, time_key)         — fan o'rtacha trend
- fact_grades (teacher_key, time_key)         — o'qituvchi reytingi
- dim_student (faculty_key, status)           — fakultet × status filter
- dim_time (year, semester)                   — semester rollup
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_perf_idx"
down_revision = "0001_olap_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === fact_grades composite indexes ===
    op.create_index("ix_fact_grades_time_student", "fact_grades", ["time_key", "student_key"])
    op.create_index("ix_fact_grades_faculty_time", "fact_grades", ["faculty_key", "time_key"])
    op.create_index("ix_fact_grades_subject_time", "fact_grades", ["subject_key", "time_key"])
    op.create_index("ix_fact_grades_teacher_time", "fact_grades", ["teacher_key", "time_key"])

    # === dim_student composite filter ===
    op.create_index("ix_dim_student_faculty_status", "dim_student", ["faculty_key", "status"])

    # === dim_time rollup ===
    op.create_index("ix_dim_time_year_semester", "dim_time", ["year", "semester"])

    # === Single-column indexes for foreign keys (often missing in star schema) ===
    for col in ("student_key", "subject_key", "teacher_key", "faculty_key", "time_key"):
        op.create_index(f"ix_fact_grades_{col}", "fact_grades", [col])


def downgrade() -> None:
    op.drop_index("ix_fact_grades_time_student", table_name="fact_grades")
    op.drop_index("ix_fact_grades_faculty_time", table_name="fact_grades")
    op.drop_index("ix_fact_grades_subject_time", table_name="fact_grades")
    op.drop_index("ix_fact_grades_teacher_time", table_name="fact_grades")
    op.drop_index("ix_dim_student_faculty_status", table_name="dim_student")
    op.drop_index("ix_dim_time_year_semester", table_name="dim_time")
    for col in ("student_key", "subject_key", "teacher_key", "faculty_key", "time_key"):
        op.drop_index(f"ix_fact_grades_{col}", table_name="fact_grades")
