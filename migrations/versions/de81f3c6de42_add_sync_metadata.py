"""add sync metadata

Revision ID: de81f3c6de42
Revises: a671d6014d0d
Create Date: 2026-11-19 21:30:07.411866

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "de81f3c6de42"
down_revision: Union[str, Sequence[str], None] = "a671d6014d0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sync_metadata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "last_sync_time",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "last_changed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("sync_status", sa.String(length=20), nullable=False),
        sa.Column("last_error", sa.String(length=2000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sync_metadata")
