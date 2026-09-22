from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.componentes.actuador import DryRunActuator
from app.componentes.clasificador import ClasificadorNulo
from app.componentes.correlador import Correlador
from app.componentes.detector_fuerza_bruta import DetectorFuerzaBruta
from app.componentes.politicas import MotorPoliticas
from app.dominio.modelos import Baneo, Incidente
from app.servicios import ProcesadorEventos


@pytest.mark.asyncio
async def test_fail2ban_transfiere_baneo_y_crea_incidente() -> None:
    motor = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(motor)
    jail_login = DryRunActuator()
    jail_principal = DryRunActuator()
    detector = DetectorFuerzaBruta(jail_login)
    procesador = ProcesadorEventos(
        Correlador(300),
        MotorPoliticas(
            jail_principal,
            umbral_eventos=5,
            ventana_segundos=60,
            duracion_segundos=600,
            lista_blanca=("127.0.0.0/8",),
        ),
        ClasificadorNulo(),
    )
    ahora = datetime.now(UTC)
    await jail_login.bloquear("192.0.2.12", ahora + timedelta(minutes=10))

    assert await detector.baneados() == ["192.0.2.12"]
    with Session(motor) as sesion:
        resultado = await procesador.procesar_baneo_fuerza_bruta("192.0.2.12", sesion)
        assert resultado.baneo_id is not None
        incidente = sesion.get(Incidente, resultado.incidente_id)
        assert incidente is not None
        assert incidente.tipo_ataque == "fuerza_bruta"
        assert incidente.severidad == 3
        assert len(sesion.exec(select(Baneo)).all()) == 1

    await detector.transferir("192.0.2.12")
    assert await detector.baneados() == []
    assert "192.0.2.12" in await jail_principal.bloqueos()


@pytest.mark.asyncio
async def test_jail_login_distingue_ips_y_no_duplica_baneos() -> None:
    jail = DryRunActuator()
    detector = DetectorFuerzaBruta(jail)
    ahora = datetime.now(UTC)
    await jail.bloquear("192.0.2.2", ahora + timedelta(minutes=10))
    await jail.bloquear("192.0.2.1", ahora + timedelta(minutes=10))
    assert await detector.baneados() == ["192.0.2.1", "192.0.2.2"]
    await detector.transferir("192.0.2.1")
    assert await detector.baneados() == ["192.0.2.2"]
