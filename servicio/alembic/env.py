from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.config import obtener_ajustes
from app.dominio.modelos import SQLModel

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", obtener_ajustes().database_url)
target_metadata = SQLModel.metadata


def preparar_directorio_sqlite(url: str) -> None:
    if url.startswith("sqlite:///"):
        ruta = url.removeprefix("sqlite:///")
        if ruta != ":memory:":
            Path(ruta).parent.mkdir(parents=True, exist_ok=True)


def ejecutar_migraciones_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def ejecutar_migraciones_online() -> None:
    preparar_directorio_sqlite(config.get_main_option("sqlalchemy.url"))
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    ejecutar_migraciones_offline()
else:
    ejecutar_migraciones_online()
