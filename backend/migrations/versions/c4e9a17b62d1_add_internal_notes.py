"""add internal notes to ticket messages

Revision ID: c4e9a17b62d1
Revises: b1d8f7a4c902
"""

from alembic import op
import sqlalchemy as sa


revision = "c4e9a17b62d1"
down_revision = "b1d8f7a4c902"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "mensagens",
        sa.Column(
            "interna",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("mensagens", "interna")
