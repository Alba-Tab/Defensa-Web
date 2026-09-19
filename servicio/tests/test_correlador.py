from datetime import datetime, timedelta

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.componentes.correlador import Correlador
from app.dominio.esquemas import EventoEntrada


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
        primero, _ = correlador.registrar(crear_evento(inicio), sesion)
        sesion.commit()
        segundo, _ = correlador.registrar(crear_evento(inicio + timedelta(seconds=301)), sesion)

        assert primero.id != segundo.id
