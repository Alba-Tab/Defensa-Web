"""Motor de políticas de bloqueo.

Pb-18: la lista blanca se lee de la tabla ``lista_blanca`` en cada evaluación.
Las redes protegidas de la configuración siempre se aplican además de las
entradas dinámicas de la tabla.
"""

from datetime import datetime, timedelta
from ipaddress import ip_address, ip_network

from sqlmodel import Session, col, select

from app.componentes.actuador import ActuadorBloqueo
from app.dominio.modelos import Auditoria, Baneo, Evento, Incidente, ListaBlanca


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
        self._redes_protegidas = tuple(ip_network(red, strict=False) for red in lista_blanca)

    def _ip_en_lista_blanca(self, origen: str, sesion: Session) -> bool:
        """Comprueba si la IP está en la lista blanca leyendo la BD (Pb-18).

        Las redes de configuración nunca dejan de estar protegidas aunque
        existan entradas dinámicas o la tabla todavía no esté sembrada.
        """
        ip = ip_address(origen)
        entradas = sesion.exec(select(ListaBlanca)).all()
        return any(ip in red for red in self._redes_protegidas) or any(
            ip in ip_network(entrada.ip_o_red, strict=False) for entrada in entradas
        )

    async def evaluar(self, incidente: Incidente, ahora: datetime, sesion: Session) -> Baneo | None:
        if self._ip_en_lista_blanca(incidente.ip_origen, sesion):
            return None

        existente = sesion.exec(
            select(Baneo)
            .where(
                Baneo.ip == incidente.ip_origen,
                col(Baneo.estado).in_(["vigente", "fallido"]),
            )
            .order_by(col(Baneo.inicio).desc())
        ).first()
        if existente is not None and existente.estado == "vigente":
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
        assert incidente.id is not None
        baneo = existente or Baneo(
            ip=incidente.ip_origen,
            expira=expira,
            incidente_id=incidente.id,
            estado="pendiente",
        )
        baneo.expira = expira
        sesion.add(baneo)
        sesion.flush()
        try:
            await self._actuador.bloquear(incidente.ip_origen, expira)
        except Exception as error:
            baneo.estado = "fallido"
            sesion.add(baneo)
            sesion.add(
                Auditoria(
                    actor="sistema",
                    accion="bloqueo_fallido",
                    ip_afectada=incidente.ip_origen,
                    detalle=str(error)[:500],
                )
            )
            sesion.flush()
            return baneo

        reintento = existente is not None
        baneo.estado = "vigente"
        sesion.add(baneo)
        sesion.add(
            Auditoria(
                actor="sistema",
                accion="bloqueo_reintentado" if reintento else "bloqueo_automatico",
                ip_afectada=incidente.ip_origen,
                detalle=f"umbral={self._umbral};duracion_segundos={int(self._duracion.total_seconds())}",
            )
        )
        sesion.flush()
        return baneo
