from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from sqlmodel import SQLModel

from app.config import Ajustes
from app.database import crear_motor
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
