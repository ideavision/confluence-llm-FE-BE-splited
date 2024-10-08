"""Payserai Custom Tool Flow

Revision ID: dba7f71618f5
Revises: d5645c915d0e
Create Date: 2023-12-18 15:18:37.370972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dba7f71618f5"
down_revision = "d5645c915d0e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "passist",
        sa.Column("retrieval_enabled", sa.Boolean(), nullable=True),
    )
    op.execute("UPDATE passist SET retrieval_enabled = true")
    op.alter_column("passist", "retrieval_enabled", nullable=False)


def downgrade() -> None:
    op.drop_column("passist", "retrieval_enabled")
