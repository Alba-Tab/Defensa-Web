from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from sqlalchemy import Engine
from sqlmodel import Session, col, select

from app.componentes.correlador import Correlador
from app.dominio.esquemas import EventoEntrada
from app.dominio.modelos import Auditoria, Baneo, Evento, Incidente, ahora_utc


class Repositorio:
    """Frontera de persistencia con una sesión corta por operación."""

    def __init__(self, motor: Engine, ventana_correlacion_segundos: int = 300) -> None:
        self._motor = motor
        self._correlador = Correlador(ventana_correlacion_segundos)

    @contextmanager
    def transaccion(self) -> Iterator[Session]:
        with Session(self._motor) as sesion:
            try:
                yield sesion
                sesion.commit()
            except Exception:
                sesion.rollback()
                raise

    def guardar_evento(self, entrada: EventoEntrada | Mapping[str, Any]) -> Evento:
        if not isinstance(entrada, EventoEntrada):
            datos = dict(entrada)
            datos.setdefault("fecha_utc", ahora_utc())
            datos.setdefault("metodo", None)
            datos.setdefault("url", None)
            entrada = EventoEntrada.model_validate(datos)

        with self.transaccion() as sesion:
            _, evento, _ = self._correlador.registrar(entrada, sesion)
            sesion.flush()
            sesion.refresh(evento)
            sesion.expunge(evento)
            return evento

    def incidente_abierto(
        self, ip: str, categoria: str, desde: datetime | None = None
    ) -> Incidente | None:
        sentencia = select(Incidente).where(
            Incidente.ip_origen == ip,
            Incidente.categoria == categoria,
            Incidente.estado == "abierto",
        )
        if desde is not None:
            sentencia = sentencia.where(Incidente.ultima_actividad >= desde)
        with Session(self._motor) as sesion:
            incidente = sesion.exec(
                sentencia.order_by(col(Incidente.ultima_actividad).desc())
            ).first()
            if incidente is not None:
                sesion.expunge(incidente)
            return incidente

    def baneos_vigentes(self) -> list[Baneo]:
        with Session(self._motor) as sesion:
            baneos = list(sesion.exec(select(Baneo).where(Baneo.estado == "vigente")).all())
            for baneo in baneos:
                sesion.expunge(baneo)
            return baneos

    def baneos_conciliables(self) -> list[Baneo]:
        with Session(self._motor) as sesion:
            baneos = list(
                sesion.exec(
                    select(Baneo).where(col(Baneo.estado).in_(["vigente", "fallido"]))
                ).all()
            )
            for baneo in baneos:
                sesion.expunge(baneo)
            return baneos

    def cambiar_estado_baneo(
        self,
        baneo_id: int,
        estado: str,
        *,
        accion: str,
        detalle: str | None = None,
    ) -> None:
        with self.transaccion() as sesion:
            baneo = sesion.get(Baneo, baneo_id)
            if baneo is None:
                raise LookupError(f"Baneo inexistente: {baneo_id}")
            baneo.estado = estado
            sesion.add(baneo)
            sesion.add(
                Auditoria(
                    actor="conciliador",
                    accion=accion,
                    ip_afectada=baneo.ip,
                    detalle=detalle,
                )
            )

    def registrar_auditoria(self, accion: str, ip: str, detalle: str | None = None) -> None:
        with self.transaccion() as sesion:
            sesion.add(
                Auditoria(
                    actor="conciliador",
                    accion=accion,
                    ip_afectada=ip,
                    detalle=detalle,
                )
            )

    def contar_eventos(self) -> int:
        with Session(self._motor) as sesion:
            return len(sesion.exec(select(Evento.id)).all())

    def cerrar_incidentes_inactivos(self, ahora: datetime) -> list[int]:
        limite = ahora - self._correlador.ventana
        cerrados: list[int] = []
        with self.transaccion() as sesion:
            candidatos = sesion.exec(
                select(Incidente).where(
                    Incidente.estado == "abierto",
                    Incidente.ultima_actividad <= limite,
                )
            ).all()
            for incidente in candidatos:
                assert incidente.id is not None
                baneo_activo = sesion.exec(
                    select(Baneo.id).where(
                        Baneo.incidente_id == incidente.id,
                        Baneo.estado == "vigente",
                        Baneo.expira > ahora,
                    )
                ).first()
                if baneo_activo is not None:
                    continue
                incidente.estado = "cerrado"
                sesion.add(incidente)
                cerrados.append(incidente.id)
        return cerrados
