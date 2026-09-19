from datetime import timedelta

from sqlmodel import Session, col, select

from app.dominio.esquemas import EventoEntrada
from app.dominio.modelos import Evento, Incidente


class Correlador:
    def __init__(self, ventana_segundos: int) -> None:
        self._ventana = timedelta(seconds=ventana_segundos)

    def registrar(self, entrada: EventoEntrada, sesion: Session) -> tuple[Incidente, Evento]:
        inicio_ventana = entrada.fecha_utc - self._ventana
        sentencia = (
            select(Incidente)
            .where(
                Incidente.ip_origen == entrada.ip_origen,
                Incidente.categoria == entrada.categoria,
                Incidente.estado == "abierto",
                Incidente.ultima_actividad >= inicio_ventana,
            )
            .order_by(col(Incidente.ultima_actividad).desc())
        )
        incidente = sesion.exec(sentencia).first()
        if incidente is None:
            incidente = Incidente(
                ip_origen=entrada.ip_origen,
                categoria=entrada.categoria,
                severidad=entrada.severidad_firma,
                inicio=entrada.fecha_utc,
                ultima_actividad=entrada.fecha_utc,
            )
            sesion.add(incidente)
            sesion.flush()
        else:
            incidente.ultima_actividad = max(incidente.ultima_actividad, entrada.fecha_utc)
            incidente.severidad = min(incidente.severidad, entrada.severidad_firma)

        assert incidente.id is not None
        evento = Evento(**entrada.model_dump(), incidente_id=incidente.id)
        sesion.add(evento)
        sesion.flush()
        return incidente, evento
