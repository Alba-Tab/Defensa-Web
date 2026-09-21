import asyncio
from contextlib import suppress
from datetime import datetime

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.componentes.informes import GeneradorPlantilla, InformeGenerado
from app.dominio.modelos import Dispositivo, Evento, Incidente
from app.integracion import enriquecer_incidentes


class NotificadorEspia:
    def __init__(self, invalidos: set[str] | None = None) -> None:
        self.llamadas: list[tuple[int, list[str]]] = []
        self._invalidos = invalidos or set()

    async def enviar(self, incidente: Incidente, tokens: list[str]) -> set[str]:
        assert incidente.id is not None
        self.llamadas.append((incidente.id, tokens))
        return self._invalidos


class GeneradorEspia:
    async def generar(self, incidente: Incidente) -> InformeGenerado:
        return InformeGenerado(
            contenido=f"Informe generado para {incidente.ip_origen}",
            origen="generado_ia",
            modelo="llama3.2:1b",
        )


class GeneradorInestable:
    def __init__(self) -> None:
        self.intentos = 0

    async def generar(self, incidente: Incidente) -> InformeGenerado:
        self.intentos += 1
        if self.intentos == 1:
            raise RuntimeError("fallo transitorio")
        return InformeGenerado(
            contenido=f"Informe recuperado para {incidente.ip_origen}",
            origen="generado_ia",
            modelo="llama3.2:1b",
        )


def preparar_incidente(sesion: Session, severidad: int, ip: str) -> Incidente:
    incidente = Incidente(
        ip_origen=ip,
        categoria="sqli",
        tipo_ataque="sqli",
        severidad=severidad,
    )
    sesion.add(incidente)
    sesion.flush()
    assert incidente.id is not None
    sesion.add(
        Evento(
            fecha_utc=datetime(2026, 9, 19, 12, 0, 0),
            ip_origen=ip,
            sid=1,
            firma="SQLi",
            categoria="sqli",
            severidad_firma=1,
            accion="descarte",
            incidente_id=incidente.id,
        )
    )
    return incidente


@pytest.mark.asyncio
async def test_incidente_alto_notifica_una_vez_y_elimina_token_invalido() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    with Session(motor) as sesion:
        incidente = preparar_incidente(sesion, 3, "192.0.2.70")
        sesion.add_all(
            [
                Dispositivo(token_fcm="token-valido-123456", plataforma="android"),
                Dispositivo(token_fcm="token-invalido-123456", plataforma="android"),
            ]
        )
        sesion.commit()
        incidente_id = incidente.id
    assert incidente_id is not None

    cola: asyncio.Queue[int] = asyncio.Queue()
    notificador = NotificadorEspia({"token-invalido-123456"})
    tarea = asyncio.create_task(
        enriquecer_incidentes(cola, motor, GeneradorPlantilla(), notificador)
    )
    try:
        await cola.put(incidente_id)
        await cola.join()
        await cola.put(incidente_id)
        await cola.join()
    finally:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea

    assert len(notificador.llamadas) == 1
    with Session(motor) as sesion:
        tokens = {dispositivo.token_fcm for dispositivo in sesion.exec(select(Dispositivo)).all()}
        persistido = sesion.get(Incidente, incidente_id)
    assert tokens == {"token-valido-123456"}
    assert persistido is not None
    assert persistido.severidad_notificada == 3


@pytest.mark.asyncio
async def test_incidente_medio_no_notifica_hasta_escalar_a_alto() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    with Session(motor) as sesion:
        incidente = preparar_incidente(sesion, 2, "192.0.2.71")
        sesion.add(Dispositivo(token_fcm="token-valido-123456", plataforma="android"))
        sesion.commit()
        incidente_id = incidente.id
    assert incidente_id is not None

    cola: asyncio.Queue[int] = asyncio.Queue()
    notificador = NotificadorEspia()
    tarea = asyncio.create_task(
        enriquecer_incidentes(
            cola,
            motor,
            GeneradorPlantilla(),
            notificador,
        )
    )
    try:
        await cola.put(incidente_id)
        await cola.join()
        assert notificador.llamadas == []

        with Session(motor) as sesion:
            persistido = sesion.get(Incidente, incidente_id)
            assert persistido is not None
            persistido.severidad = 3
            sesion.add(persistido)
            sesion.commit()
        await cola.put(incidente_id)
        await cola.join()
    finally:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea

    assert len(notificador.llamadas) == 1


@pytest.mark.asyncio
async def test_enriquecimiento_persiste_origen_y_modelo_del_informe() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    with Session(motor) as sesion:
        incidente = preparar_incidente(sesion, 2, "192.0.2.72")
        sesion.commit()
        incidente_id = incidente.id
    assert incidente_id is not None

    cola: asyncio.Queue[int] = asyncio.Queue()
    tarea = asyncio.create_task(
        enriquecer_incidentes(cola, motor, GeneradorEspia(), NotificadorEspia())
    )
    try:
        await cola.put(incidente_id)
        await cola.join()
    finally:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea

    with Session(motor) as sesion:
        persistido = sesion.get(Incidente, incidente_id)
    assert persistido is not None
    assert persistido.informe == "Informe generado para 192.0.2.72"
    assert persistido.origen_informe == "generado_ia"
    assert persistido.modelo_informe == "llama3.2:1b"


@pytest.mark.asyncio
async def test_enriquecimiento_reintenta_un_fallo_transitorio_sin_morir() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    with Session(motor) as sesion:
        incidente = preparar_incidente(sesion, 2, "192.0.2.73")
        sesion.commit()
        incidente_id = incidente.id
    assert incidente_id is not None

    generador = GeneradorInestable()
    cola: asyncio.Queue[int] = asyncio.Queue()
    tarea = asyncio.create_task(
        enriquecer_incidentes(
            cola,
            motor,
            generador,
            NotificadorEspia(),
            espera_reintento_segundos=0,
        )
    )
    try:
        await cola.put(incidente_id)
        await cola.join()
    finally:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea

    with Session(motor) as sesion:
        persistido = sesion.get(Incidente, incidente_id)
    assert generador.intentos == 2
    assert persistido is not None
    assert persistido.informe == "Informe recuperado para 192.0.2.73"
