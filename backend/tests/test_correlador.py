from datetime import datetime, timedelta

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.componentes.correlador import Correlador
from app.dominio.esquemas import EventoEntrada
from app.dominio.modelos import Incidente


def crear_evento(fecha: datetime) -> EventoEntrada:
    return EventoEntrada(
        fecha_utc=fecha,
        ip_origen="192.0.2.20",
        sid=1,
        firma="Prueba",
        categoria="sqli",
        severidad_firma=2,
    )


def test_evento_fuera_de_ventana_crea_otro_incidente() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    correlador = Correlador(ventana_segundos=300)
    inicio = datetime(2026, 9, 19, 12, 0, 0)

    with Session(motor) as sesion:
        primero, _, _ = correlador.registrar(crear_evento(inicio), sesion)
        sesion.commit()
        segundo, _, _ = correlador.registrar(crear_evento(inicio + timedelta(seconds=301)), sesion)

        assert primero.id != segundo.id


def test_agrupa_por_ip_y_categoria_y_convierte_la_severidad() -> None:
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    correlador = Correlador(ventana_segundos=300)
    inicio = datetime(2026, 9, 19, 12, 0, 0)

    with Session(motor) as sesion:
        entradas = [crear_evento(inicio + timedelta(milliseconds=indice)) for indice in range(300)]
        entradas[0].severidad_firma = 3
        entradas[-1].severidad_firma = 1
        resultados = [correlador.registrar(entrada, sesion) for entrada in entradas]
        otro_origen = crear_evento(inicio + timedelta(seconds=1))
        otro_origen.ip_origen = "192.0.2.21"
        correlador.registrar(otro_origen, sesion)
        otra_categoria = crear_evento(inicio + timedelta(seconds=1))
        otra_categoria.categoria = "escaneo"
        correlador.registrar(otra_categoria, sesion)
        sesion.commit()

        incidentes = list(sesion.exec(select(Incidente)).all())

    assert len({incidente.id for incidente, _, _ in resultados}) == 1
    assert len(incidentes) == 3
    principal = next(
        incidente
        for incidente in incidentes
        if incidente.ip_origen == "192.0.2.20" and incidente.categoria == "sqli"
    )
    assert principal.severidad == 3
