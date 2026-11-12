"""add remetente id to mensagens

Revision ID: da7f56d3c9ea
Revises: a728fb9e8225
Create Date: 2026-11-02

"""

from alembic import op
import sqlalchemy as sa


revision = "da7f56d3c9ea"
down_revision = "a728fb9e8225"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "mensagens",
        sa.Column("remetente_id", sa.Integer(), nullable=True)
    )

    op.create_foreign_key(
        "fk_mensagens_remetente_id_usuarios",
        "mensagens",
        "usuarios",
        ["remetente_id"],
        ["id"],
        ondelete="SET NULL"
    )

    op.create_index(
        "ix_mensagens_remetente_id",
        "mensagens",
        ["remetente_id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mensagens_remetente_id",
        table_name="mensagens"
    )

    op.drop_constraint(
        "fk_mensagens_remetente_id_usuarios",
        "mensagens",
        type_="foreignkey"
    )

    op.drop_column("mensagens", "remetente_id")
