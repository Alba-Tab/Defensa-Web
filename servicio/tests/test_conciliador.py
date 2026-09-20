from datetime import datetime, timedelta
from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel

from app.componentes.actuador import DryRunActuator
from app.componentes.conciliador import Conciliador, ResultadoConciliacion
from app.config import Ajustes
from app.database import crear_motor
from app.dominio.modelos import Baneo, Incidente
from app.repositorio import Repositorio


@pytest.mark.asyncio
async def test_concilia_baneos_vigentes_expirados_y_huerfanos(tmp_path: Path) -> None:
    motor = crear_motor(
        Ajustes(
            entorno="pruebas",
            database_url=f"sqlite:///{tmp_path / 'conciliacion.db'}",
        )
    )
    SQLModel.metadata.create_all(motor)
    ahora = datetime(2026, 9, 19, 12, 0, 0)
    with Session(motor) as sesion:
        incidente = Incidente(ip_origen="192.0.2.10", categoria="sqli", severidad=1)
        sesion.add(incidente)
        sesion.flush()
        assert incidente.id is not None
        sesion.add_all(
            [
                Baneo(
                    ip="192.0.2.10",
                    expira=ahora + timedelta(minutes=5),
                    incidente_id=incidente.id,
                ),
                Baneo(
                    ip="192.0.2.11",
                    expira=ahora - timedelta(seconds=1),
                    incidente_id=incidente.id,
                ),
            ]
        )
        sesion.commit()

    actuador = DryRunActuator()
    await actuador.bloquear("192.0.2.11", ahora - timedelta(seconds=1))
    await actuador.bloquear("192.0.2.99", ahora + timedelta(minutes=5))
    conciliador = Conciliador(Repositorio(motor), actuador)

    resultado = await conciliador.ejecutar(ahora)

    assert resultado == ResultadoConciliacion(
        restaurados=1,
        expirados=1,
        huerfanos_liberados=1,
        errores=0,
    )
    assert set(await actuador.bloqueos()) == {"192.0.2.10"}
    assert {baneo.ip for baneo in Repositorio(motor).baneos_vigentes()} == {"192.0.2.10"}
    motor.dispose()


@pytest.mark.asyncio
async def test_conciliador_reintenta_un_baneo_fallido(tmp_path: Path) -> None:
    motor = crear_motor(
        Ajustes(
            entorno="pruebas",
            database_url=f"sqlite:///{tmp_path / 'reintento.db'}",
        )
    )
    SQLModel.metadata.create_all(motor)
    ahora = datetime(2026, 9, 19, 12, 0, 0)
    with Session(motor) as sesion:
        incidente = Incidente(ip_origen="192.0.2.30", categoria="sqli", severidad=3)
        sesion.add(incidente)
        sesion.flush()
        assert incidente.id is not None
        sesion.add(
            Baneo(
                ip=incidente.ip_origen,
                expira=ahora + timedelta(minutes=5),
                incidente_id=incidente.id,
                estado="fallido",
            )
        )
        sesion.commit()

    actuador = DryRunActuator()
    resultado = await Conciliador(Repositorio(motor), actuador).ejecutar(ahora)

    assert resultado.restaurados == 1
    assert set(await actuador.bloqueos()) == {"192.0.2.30"}
    assert {baneo.ip for baneo in Repositorio(motor).baneos_vigentes()} == {"192.0.2.30"}
    motor.dispose()
