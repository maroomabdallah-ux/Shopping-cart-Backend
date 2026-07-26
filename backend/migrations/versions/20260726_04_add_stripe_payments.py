"""Add Stripe payment tracking to orders.

Revision ID: 20260726_04
Revises: 20260726_03
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260726_04"
down_revision: str | Sequence[str] | None = "20260726_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "order",
        sa.Column("payment_status", sa.String(30), nullable=False, server_default="unpaid"),
    )
    op.add_column(
        "order",
        sa.Column("stripe_checkout_session_id", sa.String(255), nullable=True),
    )
    op.create_index(
        "ix_order_stripe_checkout_session_id",
        "order",
        ["stripe_checkout_session_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_order_stripe_checkout_session_id", table_name="order")
    op.drop_column("order", "stripe_checkout_session_id")
    op.drop_column("order", "payment_status")
