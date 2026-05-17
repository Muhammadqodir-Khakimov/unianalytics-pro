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


TABLE = "fact_student_grades"
COMPOSITE = [
    ("ix_fact_time_student",  ["time_key", "student_key"]),
    ("ix_fact_faculty_time2", ["faculty_key", "time_key"]),
    ("ix_fact_subject_time",  ["subject_key", "time_key"]),
    ("ix_fact_teacher_time",  ["teacher_key", "time_key"]),
]
SINGLE_COLS = ("student_key", "subject_key", "teacher_key", "faculty_key", "time_key")


def upgrade() -> None:
    bind = op.get_bind()
    existing = {idx["name"] for idx in sa.inspect(bind).get_indexes(TABLE)}

    for name, cols in COMPOSITE:
        if name not in existing:
            op.create_index(name, TABLE, cols)

    # dim_time rollup (year + semester)
    if "ix_dim_time_year_semester" not in {
        idx["name"] for idx in sa.inspect(bind).get_indexes("dim_time")
    }:
        op.create_index("ix_dim_time_year_semester", "dim_time", ["year", "semester"])

    # Yagona ustun indekslari (FK)
    for col in SINGLE_COLS:
        name = f"ix_fact_{col}_perf"
        if name not in existing:
            op.create_index(name, TABLE, [col])


def downgrade() -> None:
    bind = op.get_bind()
    existing = {idx["name"] for idx in sa.inspect(bind).get_indexes(TABLE)}

    for col in SINGLE_COLS:
        name = f"ix_fact_{col}_perf"
        if name in existing:
            op.drop_index(name, table_name=TABLE)
    for name, _ in COMPOSITE:
        if name in existing:
            op.drop_index(name, table_name=TABLE)
    if "ix_dim_time_year_semester" in {
        idx["name"] for idx in sa.inspect(bind).get_indexes("dim_time")
    }:
        op.drop_index("ix_dim_time_year_semester", table_name="dim_time")
