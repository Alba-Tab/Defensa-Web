from datetime import datetime, timedelta

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.componentes.correlador import Correlador
from app.componentes.politicas import MotorPoliticas
from app.dominio.esquemas import EventoEntrada
from app.dominio.modelos import Auditoria, Baneo


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
async def test_bloqueo_progresivo_incrementa_duracion_y_severidad() -> None:
    """Pb-16: Verificar que baneos sucesivos duran más y severidad sube a crítica en el 3ro."""
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

    baneos = []

    for ataque_num in range(4):
        with Session(motor) as sesion:
            for indice in range(5):
                incidente, _, _ = correlador.registrar(
                    evento(inicio + timedelta(seconds=ataque_num*100 + indice), ataque_num*10 + indice), sesion
                )
            sesion.commit()

        with Session(motor) as sesion:
            incidente, _, _ = correlador.registrar(
                evento(inicio + timedelta(seconds=ataque_num*100 + 5), ataque_num*10 + 5), sesion
            )
            baneo = await politicas.evaluar(incidente, inicio + timedelta(seconds=ataque_num*100 + 5), sesion)
            sesion.commit()
            if baneo:
                baneos.append(baneo)

    assert len(baneos) == 4, "Debería haber 4 baneos"

    duraciones_esperadas = [
        timedelta(minutes=10),
        timedelta(minutes=20),
        timedelta(minutes=40),
        timedelta(hours=24),
    ]

    for idx, (baneo, duracion_esperada) in enumerate(zip(baneos, duraciones_esperadas)):
        duracion_real = baneo.expira - baneo.inicio
        assert duracion_real == duracion_esperada, f"Baneo {idx+1}: esperaba {duracion_esperada}, obtuvo {duracion_real}"
        assert baneo.nivel_reincidencia == idx + 1, f"Baneo {idx+1}: nivel debería ser {idx+1}"

    assert baneos[2].incidente.severidad == 4, "Tercer baneo debería marcar incidente como CRÍTICA (severidad 4)"
