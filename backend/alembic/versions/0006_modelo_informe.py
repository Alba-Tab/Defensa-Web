"""Registra el modelo que generó el informe del incidente."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_modelo_informe"
down_revision: str | None = "0005_notificacion_incidente"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("incidente") as lote:
        lote.add_column(sa.Column("modelo_informe", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("incidente") as lote:
        lote.drop_column("modelo_informe")
