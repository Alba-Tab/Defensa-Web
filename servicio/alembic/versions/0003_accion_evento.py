"""Registra si Suricata alertó o descartó la petición."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_accion_evento"
down_revision: str | None = "0002_integracion_real_movil_ia"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("evento") as lote:
        lote.add_column(sa.Column("accion", sa.String(), nullable=False, server_default="alerta"))


def downgrade() -> None:
    with op.batch_alter_table("evento") as lote:
        lote.drop_column("accion")
