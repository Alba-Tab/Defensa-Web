from pathlib import Path

from pytest import MonkeyPatch
from sqlalchemy import create_engine, inspect, text

from app.config import obtener_ajustes


def test_esquema_nuevo_llega_a_la_revision_vigente(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    from alembic import command
    from alembic.config import Config

    base = tmp_path / "migraciones.db"
    url = f"sqlite:///{base}"
    monkeypatch.setenv("DEFENSA_DATABASE_URL", url)
    obtener_ajustes.cache_clear()
    configuracion = Config(Path(__file__).parents[1] / "alembic.ini")

    try:
        command.upgrade(configuracion, "head")
    finally:
        obtener_ajustes.cache_clear()

    motor = create_engine(url)
    columnas = {columna["name"] for columna in inspect(motor).get_columns("incidente")}
    with motor.connect() as conexion:
        revision = conexion.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    motor.dispose()

    assert revision == "0006_modelo_informe"
    assert "modelo_informe" in columnas
