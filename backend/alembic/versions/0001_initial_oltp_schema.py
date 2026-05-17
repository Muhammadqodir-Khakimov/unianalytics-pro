"""Initial OLTP schema.

Revision ID: 0001_oltp_init
Revises:
Create Date: 2025-01-01 00:00:00

OLTP databazaga barcha tranzaktsion jadvallarni yaratadi.
Ishga tushirish: alembic -x target=oltp upgrade head
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_oltp_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("full_name", sa.String(256), nullable=False),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "dekan", "teacher", "student", name="user_role"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # faculties
    op.create_table(
        "faculties",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(256), unique=True, nullable=False),
        sa.Column("code", sa.String(32), unique=True, nullable=False),
        sa.Column("description", sa.String(512)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # specialties
    op.create_table(
        "specialties",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("code", sa.String(32), unique=True, nullable=False),
        sa.Column("faculty_id", sa.Integer, sa.ForeignKey("faculties.id", ondelete="CASCADE")),
    )

    # groups
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(64), unique=True, nullable=False),
        sa.Column("course", sa.Integer, nullable=False),
        sa.Column("specialty_id", sa.Integer, sa.ForeignKey("specialties.id", ondelete="CASCADE")),
        sa.Column("enrollment_year", sa.Integer, nullable=False),
    )

    # students
    op.create_table(
        "students",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("full_name", sa.String(256), nullable=False),
        sa.Column("gender", sa.Enum("M", "F", name="gender"), nullable=False),
        sa.Column("birth_date", sa.Date, nullable=False),
        sa.Column("phone", sa.String(32)),
        sa.Column("email", sa.String(128)),
        sa.Column("group_id", sa.Integer, sa.ForeignKey("groups.id")),
        sa.Column(
            "education_form",
            sa.Enum("kunduzgi", "sirtqi", "kechki", name="education_form"),
        ),
        sa.Column(
            "status",
            sa.Enum("faol", "akademik_tatil", "chetlatilgan", "bitirgan", name="student_status"),
        ),
        sa.Column("enrollment_year", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), unique=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # teachers
    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("teacher_id", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("full_name", sa.String(256), nullable=False),
        sa.Column("academic_degree", sa.String(64)),
        sa.Column("position", sa.String(128)),
        sa.Column("department", sa.String(256)),
        sa.Column("phone", sa.String(32)),
        sa.Column("email", sa.String(128)),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), unique=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # subjects
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("department", sa.String(256)),
        sa.Column("credit_hours", sa.Integer, default=3),
        sa.Column("subject_type", sa.Enum("majburiy", "tanlov", name="subject_type")),
        sa.Column("semester", sa.Integer, default=1),
        sa.Column("description", sa.String(1024)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # assessment_types
    op.create_table(
        "assessment_types",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(32), unique=True, nullable=False),
        sa.Column("description", sa.String(256)),
        sa.Column("weight_percentage", sa.Numeric(5, 2), default=25.0),
    )

    # grades
    op.create_table(
        "grades",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "student_id",
            sa.Integer,
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("subject_id", sa.Integer, sa.ForeignKey("subjects.id"), index=True),
        sa.Column("teacher_id", sa.Integer, sa.ForeignKey("teachers.id"), index=True),
        sa.Column("assessment_type_id", sa.Integer, sa.ForeignKey("assessment_types.id")),
        sa.Column("grade_value", sa.Numeric(5, 2), nullable=False),
        sa.Column("attendance_percentage", sa.Numeric(5, 2), default=100.0),
        sa.Column("is_passed", sa.Boolean, default=True),
        sa.Column("semester", sa.String(16), nullable=False),
        sa.Column("academic_year", sa.String(16), nullable=False, index=True),
        sa.Column("grade_date", sa.Date, nullable=False, index=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("grades")
    op.drop_table("assessment_types")
    op.drop_table("subjects")
    op.drop_table("teachers")
    op.drop_table("students")
    op.drop_table("groups")
    op.drop_table("specialties")
    op.drop_table("faculties")
    op.drop_table("users")
    sa.Enum(name="user_role").drop(op.get_bind())
    sa.Enum(name="gender").drop(op.get_bind())
    sa.Enum(name="education_form").drop(op.get_bind())
    sa.Enum(name="student_status").drop(op.get_bind())
    sa.Enum(name="subject_type").drop(op.get_bind())
