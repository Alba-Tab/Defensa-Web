"""Pb-18: agrega columna predeterminada a lista_blanca."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_lista_blanca_predeterminada"
down_revision: str | None = "0006_modelo_informe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("lista_blanca") as lote:
        lote.add_column(
            sa.Column(
                "predeterminada",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("lista_blanca") as lote:
        lote.drop_column("predeterminada")
