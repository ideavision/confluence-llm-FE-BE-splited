"""Add llm_model_version_override to Passist

Revision ID: baf71f781b9e
Revises: 50b683a8295c
Create Date: 2023-12-06 21:56:50.286158

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "baf71f781b9e"
down_revision = "50b683a8295c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "passist",
        sa.Column("llm_model_version_override", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("passist", "llm_model_version_override")
