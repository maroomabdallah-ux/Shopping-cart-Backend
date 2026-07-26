"""Track payment confirmation email delivery.

Revision ID: 20260726_05
Revises: 20260726_04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260726_05"
down_revision: str | None = "20260726_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "order",
        sa.Column("payment_email_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("order", "payment_email_sent_at")
