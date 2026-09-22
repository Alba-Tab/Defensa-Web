from datetime import UTC, datetime

from sqlmodel import Session, col, select

from app.componentes.clasificador import Clasificador
from app.componentes.correlador import Correlador
from app.componentes.politicas import MotorPoliticas
from app.dominio.esquemas import EventoEntrada, ResultadoProcesamiento
from app.dominio.modelos import Baneo


class ProcesadorEventos:
    def __init__(
        self, correlador: Correlador, politicas: MotorPoliticas, clasificador: Clasificador
    ) -> None:
        self._correlador = correlador
        self._politicas = politicas
        self._clasificador = clasificador

    async def procesar(self, entrada: EventoEntrada, sesion: Session) -> ResultadoProcesamiento:
        try:
            incidente, evento, nuevo = self._correlador.registrar(entrada, sesion)
            clasificacion = await self._clasificador.clasificar(entrada)
            evento.clase_ia = clasificacion.tipo
            evento.confianza_ia = clasificacion.confianza
            sesion.add(evento)
            incidente.confianza_clasificador = clasificacion.confianza
            if entrada.categoria in {"escaneo", "sondeo_archivos", "xss", "traversal"}:
                # Una firma local específica prevalece sobre la predicción de
                # la IA, que todavía no conoce la clase sondeo_archivos.
                incidente.tipo_ataque = entrada.categoria
            elif clasificacion.tipo != "indeterminado":
                incidente.tipo_ataque = clasificacion.tipo
            if clasificacion.severidad is not None:
                incidente.severidad = max(incidente.severidad, clasificacion.severidad)
            baneo = await self._politicas.evaluar(incidente, entrada.fecha_utc, sesion)
            sesion.commit()
            sesion.refresh(incidente)
            sesion.refresh(evento)
            if baneo is not None:
                sesion.refresh(baneo)
            assert incidente.id is not None
            assert evento.id is not None
            return ResultadoProcesamiento(
                incidente_id=incidente.id,
                evento_id=evento.id,
                baneo_id=baneo.id if baneo else None,
                incidente_nuevo=nuevo,
                tipo_ataque=incidente.tipo_ataque,
                severidad=incidente.severidad,
                ip_origen=incidente.ip_origen,
            )
        except Exception:
            sesion.rollback()
            raise

    async def procesar_baneo_fuerza_bruta(self, ip: str, sesion: Session) -> ResultadoProcesamiento:
        """Registra el incidente de un baneo confirmado por el jail de login."""
        ahora = datetime.now(UTC)
        entrada = EventoEntrada(
            fecha_utc=ahora,
            ip_origen=ip,
            sid=2000001,
            firma="Cinco intentos fallidos de inicio de sesión en 60 segundos",
            categoria="fuerza_bruta",
            severidad_firma=1,
            metodo="POST",
            url="/api/auth/login",
        )
        try:
            incidente, evento, nuevo = self._correlador.registrar(entrada, sesion)
            incidente.tipo_ataque = "fuerza_bruta"
            incidente.confianza_clasificador = 1.0
            evento.clase_ia = "fuerza_bruta"
            evento.confianza_ia = 1.0
            sesion.add(evento)
            baneo = await self._politicas.evaluar(
                incidente, ahora, sesion, confirmado_por_fail2ban=True
            )
            if baneo is None:
                baneo = sesion.exec(
                    select(Baneo).where(
                        Baneo.ip == ip, col(Baneo.estado).in_(["vigente", "fallido"])
                    )
                ).first()
            sesion.commit()
            assert incidente.id is not None
            assert evento.id is not None
            return ResultadoProcesamiento(
                incidente_id=incidente.id,
                evento_id=evento.id,
                baneo_id=baneo.id if baneo and baneo.estado == "vigente" else None,
                incidente_nuevo=nuevo,
                tipo_ataque=incidente.tipo_ataque,
                severidad=incidente.severidad,
                ip_origen=ip,
            )
        except Exception:
            sesion.rollback()
            raise
