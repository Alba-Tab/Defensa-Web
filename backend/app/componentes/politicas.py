from datetime import datetime, timedelta
from ipaddress import ip_address, ip_network

from sqlmodel import Session, col, select

from app.componentes.actuador import ActuadorBloqueo
from app.dominio.modelos import Auditoria, Baneo, Evento, Incidente


class MotorPoliticas:
    def __init__(
        self,
        actuador: ActuadorBloqueo,
        *,
        umbral_eventos: int,
        ventana_segundos: int,
        duracion_segundos: int,
        lista_blanca: tuple[str, ...],
    ) -> None:
        self._actuador = actuador
        self._umbral = umbral_eventos
        self._ventana = timedelta(seconds=ventana_segundos)
        self._duracion = timedelta(seconds=duracion_segundos)
        self._redes_permitidas = tuple(ip_network(red, strict=False) for red in lista_blanca)

    async def evaluar(self, incidente: Incidente, ahora: datetime, sesion: Session) -> Baneo | None:
        origen = ip_address(incidente.ip_origen)
        if any(origen in red for red in self._redes_permitidas):
            return None

        vigente = sesion.exec(
            select(Baneo).where(Baneo.ip == incidente.ip_origen, Baneo.estado == "vigente")
        ).first()
        if vigente is not None:
            return None

        desde = ahora - self._ventana
        eventos = sesion.exec(
            select(Evento).where(
                Evento.ip_origen == incidente.ip_origen,
                Evento.fecha_utc >= desde,
                col(Evento.severidad_firma) <= 2,
            )
        ).all()
        if len(eventos) < self._umbral:
            return None

        expira = ahora + self._duracion
        await self._actuador.bloquear(incidente.ip_origen, expira)
        assert incidente.id is not None
        baneo = Baneo(ip=incidente.ip_origen, expira=expira, incidente_id=incidente.id)
        sesion.add(baneo)
        sesion.add(
            Auditoria(
                actor="sistema",
                accion="bloqueo_automatico",
                ip_afectada=incidente.ip_origen,
                detalle=f"umbral={self._umbral};duracion_segundos={int(self._duracion.total_seconds())}",
            )
        )
        sesion.flush()
        return baneo
