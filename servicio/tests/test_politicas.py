from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.componentes.actuador import DryRunActuator
from app.componentes.correlador import Correlador
from app.componentes.politicas import MotorPoliticas
from app.dominio.esquemas import EventoEntrada
from app.dominio.modelos import Auditoria, Baneo, ListaBlanca


class ActuadorFallaUnaVez:
    def __init__(self) -> None:
        self.intentos = 0
        self.aplicados: dict[str, datetime] = {}

    async def bloquear(self, ip: str, expira: datetime) -> None:
        self.intentos += 1
        if self.intentos == 1:
            raise RuntimeError("firewall no disponible")
        self.aplicados[ip] = expira

    async def liberar(self, ip: str) -> None:
        self.aplicados.pop(ip, None)

    async def bloqueos(self) -> dict[str, datetime]:
        return dict(self.aplicados)


def evento(fecha: datetime, sid: int) -> EventoEntrada:
    return EventoEntrada(
        fecha_utc=fecha,
        ip_origen="192.0.2.50",
        sid=sid,
        firma="SQLi",
        categoria="sqli",
        severidad_firma=2,
    )


@pytest.mark.asyncio
async def test_baneo_fallido_se_persiste_y_se_reintenta() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    actuador = ActuadorFallaUnaVez()
    politicas = MotorPoliticas(
        actuador,
        umbral_eventos=5,
        ventana_segundos=60,
        duracion_segundos=600,
        lista_blanca=("127.0.0.0/8",),
    )
    correlador = Correlador(300)
    inicio = datetime(2026, 9, 19, 12, 0, 0)

    with Session(motor) as sesion:
        for indice in range(5):
            incidente, _, _ = correlador.registrar(
                evento(inicio + timedelta(seconds=indice), indice), sesion
            )
            baneo = await politicas.evaluar(incidente, inicio + timedelta(seconds=indice), sesion)
        sesion.commit()
        assert baneo is not None
        assert baneo.estado == "fallido"
        baneo_fallido_id = baneo.id

    with Session(motor) as sesion:
        incidente, _, _ = correlador.registrar(evento(inicio + timedelta(seconds=5), 6), sesion)
        reintentado = await politicas.evaluar(incidente, inicio + timedelta(seconds=5), sesion)
        sesion.commit()

        assert reintentado is not None
        assert reintentado.id == baneo_fallido_id
        assert reintentado.estado == "vigente"
        acciones = [auditoria.accion for auditoria in sesion.exec(select(Auditoria)).all()]

    assert actuador.intentos == 2
    assert acciones == ["bloqueo_fallido", "bloqueo_reintentado"]


@pytest.mark.asyncio
async def test_lista_blanca_alerta_pero_no_banea() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    actuador = ActuadorFallaUnaVez()
    politicas = MotorPoliticas(
        actuador,
        umbral_eventos=1,
        ventana_segundos=60,
        duracion_segundos=600,
        lista_blanca=("192.168.56.0/24", "192.168.56.1/32"),
    )
    entrada = evento(datetime(2026, 9, 19, 12, 0, 0), 1)
    entrada.ip_origen = "192.168.56.1"

    with Session(motor) as sesion:
        incidente, _, _ = Correlador(300).registrar(entrada, sesion)
        baneo = await politicas.evaluar(incidente, entrada.fecha_utc, sesion)
        sesion.commit()

        assert baneo is None
        assert len(sesion.exec(select(Baneo)).all()) == 0
    assert actuador.intentos == 0


@pytest.mark.asyncio
async def test_redes_configuradas_siguen_protegidas_con_entradas_en_bd() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    actuador = ActuadorFallaUnaVez()
    politicas = MotorPoliticas(
        actuador,
        umbral_eventos=1,
        ventana_segundos=60,
        duracion_segundos=600,
        lista_blanca=("127.0.0.0/8",),
    )
    entrada = evento(datetime(2026, 9, 19, 12, 0, 0), 1)
    entrada.ip_origen = "127.0.0.1"

    with Session(motor) as sesion:
        sesion.add(ListaBlanca(ip_o_red="10.0.0.0/8"))
        sesion.commit()
        incidente, _, _ = Correlador(300).registrar(entrada, sesion)
        baneo = await politicas.evaluar(incidente, entrada.fecha_utc, sesion)

    assert baneo is None
    assert actuador.intentos == 0


@pytest.mark.asyncio
async def test_reincidencias_duplican_hasta_tope_y_quedan_auditadas() -> None:
    motor = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(motor)
    actuador = DryRunActuator()
    politicas = MotorPoliticas(
        actuador,
        umbral_eventos=5,
        ventana_segundos=60,
        duracion_segundos=600,
        lista_blanca=("127.0.0.0/8",),
    )
    correlador = Correlador(300)
    momento = datetime(2026, 9, 19, 12, tzinfo=UTC)
    duraciones = [600, 1200, 2400, 4800, 9600, 19200, 38400, 76800, 86400, 86400]

    for nivel, segundos in enumerate(duraciones):
        with Session(motor) as sesion:
            for indice in range(5):
                incidente, _, _ = correlador.registrar(
                    evento(momento + timedelta(seconds=indice), nivel * 10 + indice), sesion
                )
            incidente.severidad = 3 if nivel < 2 else 2
            baneo = await politicas.evaluar(incidente, momento + timedelta(seconds=4), sesion)
            assert baneo is not None
            assert baneo.estado == "vigente"
            assert baneo.nivel_reincidencia == nivel
            assert baneo.expira - baneo.inicio == timedelta(seconds=segundos)
            assert incidente.severidad == (4 if nivel == 1 else (3 if nivel == 0 else 2))
            sesion.commit()
        momento += timedelta(seconds=segundos + 10)

    with Session(motor) as sesion:
        baneos = sesion.exec(select(Baneo)).all()
        auditorias = sesion.exec(select(Auditoria)).all()
    assert len(baneos) == len(duraciones)
    assert "nivel_reincidencia=9;duracion_segundos=86400" in auditorias[-1].detalle
