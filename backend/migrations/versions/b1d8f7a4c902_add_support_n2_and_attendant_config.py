"""add support n2 and attendant config

Revision ID: b1d8f7a4c902
Revises: da7f56d3c9ea
Create Date: 2026-11-02

"""

from alembic import op
import sqlalchemy as sa


revision = "b1d8f7a4c902"
down_revision = "da7f56d3c9ea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_usuarios_perfil_sistema",
        "usuarios",
        type_="check",
    )
    op.create_check_constraint(
        "ck_usuarios_perfil_sistema",
        "usuarios",
        "perfil_sistema IS NULL OR perfil_sistema IN ("
        "'administrador', 'suporte_n1', 'suporte_n2')",
    )

    op.create_table(
        "atendente_config",
        sa.Column(
            "usuario_id",
            sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "disponivel",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "capacidade_maxima",
            sa.Integer(),
            server_default="10",
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "capacidade_maxima >= 1",
            name="ck_atendente_config_capacidade_maxima",
        ),
    )

    op.execute(
        "INSERT INTO atendente_config "
        "(usuario_id, disponivel, capacidade_maxima, atualizado_em) "
        "SELECT id, TRUE, 10, NOW() FROM usuarios "
        "WHERE perfil_sistema IN ('suporte_n1', 'suporte_n2') "
        "ON CONFLICT (usuario_id) DO NOTHING"
    )


def downgrade() -> None:
    op.drop_table("atendente_config")

    # The previous schema did not distinguish N2. Convert N2 accounts to N1
    # so that the previous check constraint can be restored without data loss
    # to the user accounts themselves (the N2 distinction is not recoverable).
    op.execute(
        "UPDATE usuarios SET perfil_sistema = 'suporte_n1' "
        "WHERE perfil_sistema = 'suporte_n2'"
    )

    op.drop_constraint(
        "ck_usuarios_perfil_sistema",
        "usuarios",
        type_="check",
    )
    op.create_check_constraint(
        "ck_usuarios_perfil_sistema",
        "usuarios",
        "perfil_sistema IS NULL OR perfil_sistema IN ("
        "'administrador', 'suporte_n1')",
    )
