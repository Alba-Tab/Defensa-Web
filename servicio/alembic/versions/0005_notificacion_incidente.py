"""Evita notificaciones push duplicadas por incidente."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_notificacion_incidente"
down_revision: str | None = "0004_entradas_clasificador"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("incidente") as lote:
        lote.add_column(sa.Column("severidad_notificada", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("incidente") as lote:
        lote.drop_column("severidad_notificada")
