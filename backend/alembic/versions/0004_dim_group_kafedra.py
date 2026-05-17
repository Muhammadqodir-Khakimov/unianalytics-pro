"""Add dim_kafedra and dim_group, link to fact_student_grades.

Revision ID: 0004_dim_grp_kaf
Revises: 0003_mv
Create Date: 2026-05-17

TZ 6.2.2 muvofiqligi: 7-dimensionga to'liq mos kelishi uchun
dim_kafedra va dim_group jadvallari qo'shildi. fact_student_grades
ga ikkita nullable FK qo'shildi (eski yozuvlarni buzmaslik uchun).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_dim_grp_kaf"
down_revision: Union[str, None] = "0003_mv"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # dim_kafedra
    op.create_table(
        "dim_kafedra",
        sa.Column("kafedra_key", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("kafedra_kodi", sa.String(20), nullable=False, unique=True),
        sa.Column("kafedra_nomi", sa.String(200), nullable=False),
        sa.Column("faculty_key", sa.Integer, sa.ForeignKey("dim_faculty.faculty_key"), nullable=False),
        sa.Column("mudir_fish", sa.String(200)),
        sa.Column("loaded_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_dim_kafedra_kod", "dim_kafedra", ["kafedra_kodi"])
    op.create_index("ix_dim_kafedra_fakultet", "dim_kafedra", ["faculty_key"])

    # dim_group
    op.create_table(
        "dim_group",
        sa.Column("group_key", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("guruh_kodi", sa.String(20), nullable=False, unique=True),
        sa.Column("guruh_nomi", sa.String(50), nullable=False),
        sa.Column("kurs", sa.Integer, nullable=False),
        sa.Column("kafedra_key", sa.Integer, sa.ForeignKey("dim_kafedra.kafedra_key"), nullable=False),
        sa.Column("talabalar_soni", sa.Integer, server_default="0"),
        sa.Column("faol", sa.Boolean, server_default=sa.true()),
        sa.Column("loaded_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_dim_group_kod", "dim_group", ["guruh_kodi"])
    op.create_index("ix_dim_group_kafedra", "dim_group", ["kafedra_key"])
    op.create_index("ix_dim_group_kurs", "dim_group", ["kurs"])

    # fact_student_grades — yangi FK ustunlar (nullable, eski yozuvlar uchun).
    # SQLite ALTER TABLE FK qo'shilishini cheklaydi — shuning uchun ustun
    # toza Integer sifatida qo'shiladi, FK constraint esa faqat PostgreSQL'da.
    op.add_column("fact_student_grades", sa.Column("kafedra_key", sa.Integer))
    op.add_column("fact_student_grades", sa.Column("group_key", sa.Integer))

    if op.get_bind().dialect.name == "postgresql":
        op.create_foreign_key(
            "fk_fact_kafedra",
            "fact_student_grades", "dim_kafedra",
            ["kafedra_key"], ["kafedra_key"],
        )
        op.create_foreign_key(
            "fk_fact_group",
            "fact_student_grades", "dim_group",
            ["group_key"], ["group_key"],
        )

    op.create_index("ix_fact_kafedra_key", "fact_student_grades", ["kafedra_key"])
    op.create_index("ix_fact_group_key", "fact_student_grades", ["group_key"])
    op.create_index("ix_fact_kafedra_time", "fact_student_grades", ["kafedra_key", "time_key"])
    op.create_index("ix_fact_group_time", "fact_student_grades", ["group_key", "time_key"])


def downgrade() -> None:
    op.drop_index("ix_fact_group_time", table_name="fact_student_grades")
    op.drop_index("ix_fact_kafedra_time", table_name="fact_student_grades")
    op.drop_index("ix_fact_group_key", table_name="fact_student_grades")
    op.drop_index("ix_fact_kafedra_key", table_name="fact_student_grades")
    if op.get_bind().dialect.name == "postgresql":
        op.drop_constraint("fk_fact_group", "fact_student_grades", type_="foreignkey")
        op.drop_constraint("fk_fact_kafedra", "fact_student_grades", type_="foreignkey")
    op.drop_column("fact_student_grades", "group_key")
    op.drop_column("fact_student_grades", "kafedra_key")

    op.drop_index("ix_dim_group_kurs", table_name="dim_group")
    op.drop_index("ix_dim_group_kafedra", table_name="dim_group")
    op.drop_index("ix_dim_group_kod", table_name="dim_group")
    op.drop_table("dim_group")

    op.drop_index("ix_dim_kafedra_fakultet", table_name="dim_kafedra")
    op.drop_index("ix_dim_kafedra_kod", table_name="dim_kafedra")
    op.drop_table("dim_kafedra")
