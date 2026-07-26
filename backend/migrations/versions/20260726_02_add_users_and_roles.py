"""Add users and connect orders to their owners.

Revision ID: 20260726_02
Revises: 20260723_01
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.core.config import get_settings
from app.core.security import hash_password

revision: str = "20260726_02"
down_revision: str | Sequence[str] | None = "20260723_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    user = op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    settings = get_settings()
    op.bulk_insert(
        user,
        [
            {
                "name": "Administrator",
                "email": settings.admin_email.strip().lower(),
                "password_hash": hash_password(settings.admin_password),
                "role": "admin",
                "is_active": True,
            }
        ],
    )

    op.add_column("order", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_order_user_id",
        "order",
        "user",
        ["user_id"],
        ["id"],
    )
    op.create_index("ix_order_user_id", "order", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_order_user_id", table_name="order")
    op.drop_constraint("fk_order_user_id", "order", type_="foreignkey")
    op.drop_column("order", "user_id")
    op.drop_table("user")
