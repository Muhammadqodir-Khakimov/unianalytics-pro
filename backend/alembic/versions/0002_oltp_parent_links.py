"""Parent links + user preferences (OLTP).

Revision ID: 0002_oltp_parent
Revises: 0001_oltp_init
Create Date: 2026-05-17

TZ 4.2.4 talab qilgan ota-ona <-> talaba bog'lanishi va
foydalanuvchi sozlamalari (dayjest, til, push) jadvallari.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_oltp_parent"
down_revision: Union[str, None] = "0001_oltp_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    parent_status = sa.Enum(
        "pending", "approved", "rejected", "revoked",
        name="parent_link_status",
    )

    op.create_table(
        "parent_links",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "parent_user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "student_id",
            sa.Integer,
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", parent_status, nullable=False, server_default="pending"),
        sa.Column(
            "requested_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("decided_at", sa.DateTime),
        sa.Column(
            "decided_by_student",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("note", sa.String(256)),
        sa.UniqueConstraint("parent_user_id", "student_id", name="uq_parent_student"),
    )
    op.create_index("ix_parent_link_status", "parent_links", ["status"])
    op.create_index("ix_parent_link_student", "parent_links", ["student_id"])

    op.create_table(
        "user_preferences",
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "weekly_digest_enabled",
            sa.Boolean,
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "notify_new_grade",
            sa.Boolean,
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "notify_academic_risk",
            sa.Boolean,
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "language",
            sa.String(8),
            nullable=False,
            server_default="uz_lat",
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("user_preferences")

    op.drop_index("ix_parent_link_student", table_name="parent_links")
    op.drop_index("ix_parent_link_status", table_name="parent_links")
    op.drop_table("parent_links")
    sa.Enum(name="parent_link_status").drop(op.get_bind(), checkfirst=True)
