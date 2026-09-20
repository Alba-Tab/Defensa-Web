"""Persiste entradas y salida del clasificador por evento."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_entradas_clasificador"
down_revision: str | None = "0003_accion_evento"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("evento") as lote:
        lote.add_column(sa.Column("uri_decodificada", sa.String(), nullable=True))
        lote.add_column(sa.Column("parametros", sa.String(), nullable=True))
        lote.add_column(sa.Column("cuerpo_fragmento", sa.Text(), nullable=True))
        lote.add_column(sa.Column("user_agent", sa.String(), nullable=True))
        lote.add_column(sa.Column("clase_ia", sa.String(), nullable=True))
        lote.add_column(sa.Column("confianza_ia", sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("evento") as lote:
        lote.drop_column("confianza_ia")
        lote.drop_column("clase_ia")
        lote.drop_column("user_agent")
        lote.drop_column("cuerpo_fragmento")
        lote.drop_column("parametros")
        lote.drop_column("uri_decodificada")
