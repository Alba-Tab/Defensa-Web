from datetime import timedelta

from sqlmodel import Session, col, select

from app.dominio.esquemas import EventoEntrada
from app.dominio.modelos import Evento, Incidente


class Correlador:
    def __init__(self, ventana_segundos: int) -> None:
        self._ventana = timedelta(seconds=ventana_segundos)

    @property
    def ventana(self) -> timedelta:
        return self._ventana

    def registrar(self, entrada: EventoEntrada, sesion: Session) -> tuple[Incidente, Evento, bool]:
        severidad_incidente = 4 - entrada.severidad_firma
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
        nuevo = incidente is None
        if incidente is None:
            incidente = Incidente(
                ip_origen=entrada.ip_origen,
                categoria=entrada.categoria,
                severidad=severidad_incidente,
                inicio=entrada.fecha_utc,
                ultima_actividad=entrada.fecha_utc,
            )
            sesion.add(incidente)
            sesion.flush()
        else:
            incidente.ultima_actividad = max(incidente.ultima_actividad, entrada.fecha_utc)
            incidente.severidad = max(incidente.severidad, severidad_incidente)

        assert incidente.id is not None
        evento = Evento(**entrada.model_dump(), incidente_id=incidente.id)
        sesion.add(evento)
        sesion.flush()
        return incidente, evento, nuevo
