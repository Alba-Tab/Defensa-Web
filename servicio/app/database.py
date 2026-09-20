from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import Engine, event
from sqlmodel import Session, create_engine

from app.config import Ajustes


def crear_motor(ajustes: Ajustes) -> Engine:
    if ajustes.database_url.startswith("sqlite:///"):
        ruta = ajustes.database_url.removeprefix("sqlite:///")
        if ruta != ":memory:":
            Path(ruta).parent.mkdir(parents=True, exist_ok=True)

    motor = create_engine(
        ajustes.database_url,
        connect_args={"check_same_thread": False}
        if ajustes.database_url.startswith("sqlite")
        else {},
    )
    if ajustes.database_url.startswith("sqlite"):

        @event.listens_for(motor, "connect")
        def configurar_sqlite(dbapi_connection: object, _: object) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return motor


def proveedor_sesion(motor: Engine) -> Iterator[Session]:
    with Session(motor) as sesion:
        yield sesion
