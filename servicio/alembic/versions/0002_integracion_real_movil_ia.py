"""Agrega enriquecimiento de incidentes y estado del dispositivo."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_integracion_real_movil_ia"
down_revision: str | None = "0001_base_inicial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("incidente") as lote:
        lote.add_column(sa.Column("confianza_clasificador", sa.Float(), nullable=True))
        lote.add_column(sa.Column("categoria_owasp", sa.String(), nullable=True))
        lote.add_column(sa.Column("informe", sa.String(), nullable=True))
        lote.add_column(sa.Column("origen_informe", sa.String(), nullable=True))
    with op.batch_alter_table("dispositivo") as lote:
        lote.add_column(sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    with op.batch_alter_table("dispositivo") as lote:
        lote.drop_column("activo")
    with op.batch_alter_table("incidente") as lote:
        lote.drop_column("origen_informe")
        lote.drop_column("informe")
        lote.drop_column("categoria_owasp")
        lote.drop_column("confianza_clasificador")
