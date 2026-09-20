import logging
from dataclasses import dataclass
from datetime import datetime

from app.componentes.actuador import ActuadorBloqueo
from app.dominio.modelos import ahora_utc
from app.repositorio import Repositorio

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoConciliacion:
    restaurados: int = 0
    expirados: int = 0
    huerfanos_liberados: int = 0
    errores: int = 0


class Conciliador:
    """Alinea la BD con el jail exclusivo de la plataforma al arrancar."""

    def __init__(self, repositorio: Repositorio, actuador: ActuadorBloqueo) -> None:
        self._repositorio = repositorio
        self._actuador = actuador

    async def ejecutar(self, ahora: datetime | None = None) -> ResultadoConciliacion:
        instante = ahora or ahora_utc()
        try:
            reales = await self._actuador.bloqueos()
        except Exception:
            logger.exception("No se pudo consultar el estado del firewall")
            return ResultadoConciliacion(errores=1)

        restaurados = 0
        expirados = 0
        huerfanos = 0
        errores = 0
        vigentes = self._repositorio.baneos_vigentes()
        ips_vigentes = {baneo.ip for baneo in vigentes if baneo.expira > instante}

        for baneo in vigentes:
            assert baneo.id is not None
            if baneo.expira <= instante:
                try:
                    if baneo.ip in reales:
                        await self._actuador.liberar(baneo.ip)
                        reales.pop(baneo.ip, None)
                    self._repositorio.cambiar_estado_baneo(
                        baneo.id,
                        "expirado",
                        accion="conciliacion_expirado",
                    )
                    expirados += 1
                except Exception as error:
                    errores += 1
                    logger.exception("No se pudo expirar el baneo %s", baneo.id)
                    self._marcar_fallido(baneo.id, error)
            elif baneo.ip not in reales:
                try:
                    await self._actuador.bloquear(baneo.ip, baneo.expira)
                    self._repositorio.registrar_auditoria("conciliacion_restaurado", baneo.ip)
                    restaurados += 1
                except Exception as error:
                    errores += 1
                    logger.exception("No se pudo restaurar el baneo %s", baneo.id)
                    self._marcar_fallido(baneo.id, error)

        for ip in set(reales) - ips_vigentes:
            try:
                await self._actuador.liberar(ip)
                self._repositorio.registrar_auditoria("conciliacion_huerfano_liberado", ip)
                huerfanos += 1
            except Exception:
                errores += 1
                logger.exception("No se pudo liberar el bloqueo huérfano %s", ip)

        return ResultadoConciliacion(
            restaurados=restaurados,
            expirados=expirados,
            huerfanos_liberados=huerfanos,
            errores=errores,
        )

    def _marcar_fallido(self, baneo_id: int, error: Exception) -> None:
        try:
            self._repositorio.cambiar_estado_baneo(
                baneo_id,
                "fallido",
                accion="conciliacion_fallida",
                detalle=str(error)[:500],
            )
        except Exception:
            logger.exception("Tampoco se pudo persistir el fallo del baneo %s", baneo_id)
