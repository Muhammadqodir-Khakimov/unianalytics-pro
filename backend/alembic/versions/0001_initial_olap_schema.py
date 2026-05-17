"""Initial OLAP star schema.

Revision ID: 0001_olap_init
Revises:
Create Date: 2025-01-01 00:00:00

OLAP databazaga star schema (fact + 6 dimensions) yaratadi.
Ishga tushirish: alembic -x target=olap upgrade head
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_olap_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # dim_student
    op.create_table(
        "dim_student",
        sa.Column("student_key", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.String(32), nullable=False),
        sa.Column("full_name", sa.String(256), nullable=False),
        sa.Column("gender", sa.CHAR(1), nullable=False),
        sa.Column("birth_date", sa.Date),
        sa.Column("enrollment_year", sa.Integer, nullable=False),
        sa.Column("group_name", sa.String(64), nullable=False),
        sa.Column("education_form", sa.String(16)),
        sa.Column("status", sa.String(32)),
        sa.Column("loaded_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_dim_student_id", "dim_student", ["student_id"])
    op.create_index("ix_dim_student_group", "dim_student", ["group_name"])

    # dim_subject
    op.create_table(
        "dim_subject",
        sa.Column("subject_key", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("subject_code", sa.String(32), nullable=False),
        sa.Column("subject_name", sa.String(256), nullable=False),
        sa.Column("department", sa.String(256)),
        sa.Column("credit_hours", sa.Integer, default=3),
        sa.Column("subject_type", sa.String(16)),
        sa.Column("semester", sa.Integer, default=1),
        sa.Column("loaded_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_dim_subject_code", "dim_subject", ["subject_code"])
    op.create_index("ix_dim_subject_dept", "dim_subject", ["department"])

    # dim_teacher
    op.create_table(
        "dim_teacher",
        sa.Column("teacher_key", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("teacher_id", sa.String(32), nullable=False),
        sa.Column("full_name", sa.String(256), nullable=False),
        sa.Column("academic_degree", sa.String(64)),
        sa.Column("position", sa.String(128)),
        sa.Column("department", sa.String(256)),
        sa.Column("loaded_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_dim_teacher_id", "dim_teacher", ["teacher_id"])

    # dim_time
    op.create_table(
        "dim_time",
        sa.Column("time_key", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("full_date", sa.Date, nullable=False, unique=True),
        sa.Column("day", sa.Integer, nullable=False),
        sa.Column("week", sa.Integer, nullable=False),
        sa.Column("month", sa.Integer, nullable=False),
        sa.Column("month_name", sa.String(16), nullable=False),
        sa.Column("quarter", sa.Integer, nullable=False),
        sa.Column("semester", sa.String(16), nullable=False),
        sa.Column("academic_year", sa.String(16), nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
    )
    op.create_index("ix_dim_time_year", "dim_time", ["year"])
    op.create_index("ix_dim_time_academic_year", "dim_time", ["academic_year"])
    op.create_index("ix_dim_time_semester", "dim_time", ["semester"])

    # dim_faculty
    op.create_table(
        "dim_faculty",
        sa.Column("faculty_key", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("faculty_name", sa.String(256), nullable=False),
        sa.Column("department", sa.String(256)),
        sa.Column("specialty", sa.String(256), nullable=False),
        sa.Column("course", sa.Integer, nullable=False),
        sa.Column("group_name", sa.String(64), nullable=False),
        sa.Column("loaded_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_dim_faculty_name", "dim_faculty", ["faculty_name"])
    op.create_index("ix_dim_faculty_group", "dim_faculty", ["group_name"])

    # dim_assessment_type
    op.create_table(
        "dim_assessment_type",
        sa.Column("assessment_type_key", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("type_name", sa.String(32), unique=True, nullable=False),
        sa.Column("weight_percentage", sa.Numeric(5, 2), default=25.0),
        sa.Column("description", sa.String(256)),
    )

    # fact_student_grades
    op.create_table(
        "fact_student_grades",
        sa.Column("grade_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("student_key", sa.Integer, sa.ForeignKey("dim_student.student_key"), nullable=False),
        sa.Column("subject_key", sa.Integer, sa.ForeignKey("dim_subject.subject_key"), nullable=False),
        sa.Column("teacher_key", sa.Integer, sa.ForeignKey("dim_teacher.teacher_key"), nullable=False),
        sa.Column("time_key", sa.Integer, sa.ForeignKey("dim_time.time_key"), nullable=False),
        sa.Column("faculty_key", sa.Integer, sa.ForeignKey("dim_faculty.faculty_key"), nullable=False),
        sa.Column(
            "assessment_type_key",
            sa.Integer,
            sa.ForeignKey("dim_assessment_type.assessment_type_key"),
            nullable=False,
        ),
        sa.Column("grade_value", sa.Numeric(5, 2), nullable=False),
        sa.Column("credit_hours", sa.Integer, default=3),
        sa.Column("attendance_percentage", sa.Numeric(5, 2), default=100.0),
        sa.Column("gpa_points", sa.Numeric(3, 2), default=0.0),
        sa.Column("is_passed", sa.Boolean, default=True),
    )
    op.create_index("ix_fact_student_key", "fact_student_grades", ["student_key"])
    op.create_index("ix_fact_subject_key", "fact_student_grades", ["subject_key"])
    op.create_index("ix_fact_time_key", "fact_student_grades", ["time_key"])
    op.create_index("ix_fact_faculty_key", "fact_student_grades", ["faculty_key"])
    op.create_index("ix_fact_faculty_time", "fact_student_grades", ["faculty_key", "time_key"])
    op.create_index("ix_fact_student_time", "fact_student_grades", ["student_key", "time_key"])


def downgrade() -> None:
    op.drop_table("fact_student_grades")
    op.drop_table("dim_assessment_type")
    op.drop_table("dim_faculty")
    op.drop_table("dim_time")
    op.drop_table("dim_teacher")
    op.drop_table("dim_subject")
    op.drop_table("dim_student")
