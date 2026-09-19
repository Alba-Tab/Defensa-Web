"""Crea el modelo base anterior al Sprint 1."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_base_inicial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("hash_contrasena", sa.String(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("nombre"),
    )
    op.create_table(
        "incidente",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ip_origen", sa.String(), nullable=False),
        sa.Column("categoria", sa.String(), nullable=False),
        sa.Column("tipo_ataque", sa.String(), nullable=False),
        sa.Column("severidad", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(), nullable=False),
        sa.Column("inicio", sa.DateTime(), nullable=False),
        sa.Column("ultima_actividad", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_incidente_ip_origen", "incidente", ["ip_origen"])
    op.create_index("ix_incidente_ultima_actividad", "incidente", ["ultima_actividad"])
    op.create_table(
        "evento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fecha_utc", sa.DateTime(), nullable=False),
        sa.Column("ip_origen", sa.String(), nullable=False),
        sa.Column("sid", sa.Integer(), nullable=False),
        sa.Column("firma", sa.String(), nullable=False),
        sa.Column("categoria", sa.String(), nullable=False),
        sa.Column("severidad_firma", sa.Integer(), nullable=False),
        sa.Column("metodo", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("incidente_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["incidente_id"], ["incidente.id"]),
    )
    op.create_index("ix_evento_fecha_utc", "evento", ["fecha_utc"])
    op.create_index("ix_evento_ip_origen", "evento", ["ip_origen"])
    op.create_table(
        "baneo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ip", sa.String(), nullable=False),
        sa.Column("inicio", sa.DateTime(), nullable=False),
        sa.Column("expira", sa.DateTime(), nullable=False),
        sa.Column("estado", sa.String(), nullable=False),
        sa.Column("nivel_reincidencia", sa.Integer(), nullable=False),
        sa.Column("incidente_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["incidente_id"], ["incidente.id"]),
    )
    op.create_index("ix_baneo_ip", "baneo", ["ip"])
    op.create_index(
        "uq_baneo_ip_vigente",
        "baneo",
        ["ip"],
        unique=True,
        sqlite_where=sa.text("estado = 'vigente'"),
    )
    op.create_table(
        "lista_blanca",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ip_o_red", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=True),
        sa.UniqueConstraint("ip_o_red"),
    )
    op.create_table(
        "dispositivo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token_fcm", sa.String(), nullable=False),
        sa.Column("plataforma", sa.String(), nullable=False),
        sa.Column("alta", sa.DateTime(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"]),
        sa.UniqueConstraint("token_fcm"),
    )
    op.create_table(
        "auditoria",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fecha_utc", sa.DateTime(), nullable=False),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("accion", sa.String(), nullable=False),
        sa.Column("ip_afectada", sa.String(), nullable=True),
        sa.Column("detalle", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("auditoria")
    op.drop_table("dispositivo")
    op.drop_table("lista_blanca")
    op.drop_index("uq_baneo_ip_vigente", table_name="baneo")
    op.drop_index("ix_baneo_ip", table_name="baneo")
    op.drop_table("baneo")
    op.drop_index("ix_evento_ip_origen", table_name="evento")
    op.drop_index("ix_evento_fecha_utc", table_name="evento")
    op.drop_table("evento")
    op.drop_index("ix_incidente_ultima_actividad", table_name="incidente")
    op.drop_index("ix_incidente_ip_origen", table_name="incidente")
    op.drop_table("incidente")
    op.drop_table("usuario")
