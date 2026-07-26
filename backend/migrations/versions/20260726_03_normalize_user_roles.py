"""Normalize user role values to lowercase enum values.

Revision ID: 20260726_03
Revises: 20260726_02
Create Date: 2026-07-26
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260726_03"
down_revision: str | Sequence[str] | None = "20260726_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('UPDATE "user" SET role = lower(role)')


def downgrade() -> None:
    op.execute('UPDATE "user" SET role = upper(role)')
