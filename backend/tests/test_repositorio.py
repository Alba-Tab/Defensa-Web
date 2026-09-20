from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

from sqlmodel import Session, SQLModel

from app.config import Ajustes
from app.database import crear_motor
from app.dominio.modelos import Baneo, Incidente
from app.repositorio import Repositorio


def test_escrituras_concurrentes_terminan_sin_bloqueos(tmp_path: Path) -> None:
    motor = crear_motor(
        Ajustes(
            entorno="pruebas",
            database_url=f"sqlite:///{tmp_path / 'concurrencia.db'}",
        )
    )
    SQLModel.metadata.create_all(motor)
    repositorio = Repositorio(motor)

    def escribir(indice: int) -> None:
        repositorio.guardar_evento(
            {
                "ip_origen": "192.0.2.1",
                "sid": indice,
                "firma": "Prueba concurrente",
                "categoria": "sqli",
                "severidad_firma": 1,
            }
        )

    with ThreadPoolExecutor(max_workers=8) as ejecutor:
        list(ejecutor.map(escribir, range(200)))

    assert repositorio.contar_eventos() == 200
    motor.dispose()


def test_cierra_solo_incidentes_inactivos_sin_baneo_vigente(tmp_path: Path) -> None:
    motor = crear_motor(
        Ajustes(
            entorno="pruebas",
            database_url=f"sqlite:///{tmp_path / 'cierre.db'}",
        )
    )
    SQLModel.metadata.create_all(motor)
    ahora = datetime(2026, 9, 19, 12, 10, 0)
    with Session(motor) as sesion:
        cerrable = Incidente(
            ip_origen="192.0.2.10",
            categoria="sqli",
            severidad=3,
            ultima_actividad=ahora - timedelta(minutes=6),
        )
        protegido = Incidente(
            ip_origen="192.0.2.11",
            categoria="sqli",
            severidad=3,
            ultima_actividad=ahora - timedelta(minutes=6),
        )
        reciente = Incidente(
            ip_origen="192.0.2.12",
            categoria="sqli",
            severidad=3,
            ultima_actividad=ahora - timedelta(minutes=4),
        )
        sesion.add_all([cerrable, protegido, reciente])
        sesion.flush()
        assert protegido.id is not None
        sesion.add(
            Baneo(
                ip=protegido.ip_origen,
                incidente_id=protegido.id,
                expira=ahora + timedelta(minutes=1),
            )
        )
        sesion.commit()
        ids = {"cerrable": cerrable.id, "protegido": protegido.id, "reciente": reciente.id}

    cerrados = Repositorio(motor).cerrar_incidentes_inactivos(ahora)

    with Session(motor) as sesion:
        estados = {
            nombre: sesion.get(Incidente, identificador).estado
            for nombre, identificador in ids.items()
        }
    assert cerrados == [ids["cerrable"]]
    assert estados == {
        "cerrable": "cerrado",
        "protegido": "abierto",
        "reciente": "abierto",
    }
    motor.dispose()
