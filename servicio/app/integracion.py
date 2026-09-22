import asyncio
import logging
from contextlib import suppress

from sqlalchemy import Engine
from sqlmodel import Session, col, select

from app.componentes.conciliador import Conciliador
from app.componentes.eventos_tiempo_real import AlertaIncidente, BusEventos
from app.componentes.detector_fuerza_bruta import DetectorFuerzaBruta
from app.componentes.fuente_eventos import FuenteEventos
from app.componentes.informes import GeneradorInformes
from app.componentes.notificador import Notificador
from app.dominio.esquemas import EventoEntrada, ResultadoProcesamiento
from app.dominio.modelos import Dispositivo, Incidente, ahora_utc
from app.repositorio import Repositorio
from app.servicios import ProcesadorEventos

logger = logging.getLogger(__name__)


async def consumir_eventos(
    fuente: FuenteEventos,
    procesador: ProcesadorEventos,
    motor: Engine,
    cola_enriquecimiento: asyncio.Queue[int],
    bus_eventos: BusEventos,
) -> None:
    cola_ingesta: asyncio.Queue[EventoEntrada] = asyncio.Queue(maxsize=1000)

    async def procesar_cola() -> None:
        while True:
            evento = await cola_ingesta.get()
            try:
                with Session(motor) as sesion:
                    resultado = await procesador.procesar(evento, sesion)
                publicar_incidente_nuevo(resultado, bus_eventos)
                await cola_enriquecimiento.put(resultado.incidente_id)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("No se pudo procesar un evento de eve.json")
            finally:
                cola_ingesta.task_done()

    trabajador = asyncio.create_task(procesar_cola(), name="procesar-eventos-eve")
    try:
        async for evento in fuente.eventos():
            await cola_ingesta.put(evento)
    finally:
        await cancelar_tarea(trabajador)


async def mantener_estado(
    repositorio: Repositorio,
    conciliador: Conciliador,
    cola_enriquecimiento: asyncio.Queue[int],
    intervalo_segundos: float = 5,
) -> None:
    while True:
        await asyncio.sleep(intervalo_segundos)
        await conciliador.ejecutar()
        cerrados = repositorio.cerrar_incidentes_inactivos(ahora_utc())
        for incidente_id in cerrados:
            await cola_enriquecimiento.put(incidente_id)


async def procesar_fuerza_bruta(
    detector: DetectorFuerzaBruta,
    procesador: ProcesadorEventos,
    motor: Engine,
    cola_enriquecimiento: asyncio.Queue[int],
    bus_eventos: BusEventos,
    intervalo_segundos: float = 30,
) -> None:
    """Detecta intentos de fuerza bruta periódicamente (Pb-17)."""
    while True:
        await asyncio.sleep(intervalo_segundos)
        try:
            eventos = await detector.procesar()
            for evento in eventos:
                with Session(motor) as sesion:
                    resultado = await procesador.procesar(evento, sesion)
                publicar_incidente_nuevo(resultado, bus_eventos)
                await cola_enriquecimiento.put(resultado.incidente_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Error procesando detección de fuerza bruta")


def categoria_owasp(tipo: str, categoria_firma: str) -> str:
    normalizado = f"{tipo} {categoria_firma}".lower()
    if any(valor in normalizado for valor in ("sqli", "xss", "injection")):
        return "A05:2025 - Injection"
    if any(valor in normalizado for valor in ("traversal", "path")):
        return "A01:2025 - Broken Access Control"
    if "fuerza_bruta" in normalizado or "brute" in normalizado:
        return "A07:2025 - Authentication Failures"
    return "A09:2025 - Security Logging and Alerting Failures"


async def enriquecer_incidentes(
    cola: asyncio.Queue[int],
    motor: Engine,
    generador: GeneradorInformes,
    notificador: Notificador,
    max_reintentos: int = 3,
    espera_reintento_segundos: float = 0.25,
) -> None:
    intentos: dict[int, int] = {}
    while True:
        incidente_id = await cola.get()
        try:
            with Session(motor) as sesion:
                incidente = sesion.get(Incidente, incidente_id)
                if incidente is None:
                    continue
                incidente.categoria_owasp = categoria_owasp(
                    incidente.tipo_ataque, incidente.categoria
                )
                _ = list(incidente.eventos)
                _ = list(incidente.baneos)
                sesion.expunge(incidente)

            resultado_informe = await generador.generar(incidente)
            with Session(motor) as sesion:
                persistido = sesion.get(Incidente, incidente_id)
                if persistido is None:
                    continue
                persistido.categoria_owasp = incidente.categoria_owasp
                persistido.informe = resultado_informe.contenido
                persistido.origen_informe = resultado_informe.origen
                persistido.modelo_informe = resultado_informe.modelo
                sesion.add(persistido)
                sesion.commit()
                sesion.refresh(persistido)

                debe_notificar = persistido.severidad >= 3 and (
                    persistido.severidad_notificada is None or persistido.severidad_notificada < 3
                )
                if debe_notificar:
                    dispositivos = sesion.exec(
                        select(Dispositivo).where(col(Dispositivo.activo).is_(True))
                    ).all()
                    invalidos = await notificador.enviar(
                        persistido, [dispositivo.token_fcm for dispositivo in dispositivos]
                    )
                    for dispositivo in dispositivos:
                        if dispositivo.token_fcm in invalidos:
                            sesion.delete(dispositivo)
                    persistido.severidad_notificada = persistido.severidad
                    sesion.add(persistido)
                    sesion.commit()
            intentos.pop(incidente_id, None)
        except asyncio.CancelledError:
            raise
        except Exception:
            intento = intentos.get(incidente_id, 0) + 1
            if intento < max_reintentos:
                intentos[incidente_id] = intento
                logger.warning(
                    "No se pudo enriquecer el incidente %s; reintento %s de %s",
                    incidente_id,
                    intento,
                    max_reintentos - 1,
                    exc_info=True,
                )
                await asyncio.sleep(espera_reintento_segundos * intento)
                await cola.put(incidente_id)
            else:
                intentos.pop(incidente_id, None)
                logger.exception(
                    "No se pudo enriquecer el incidente %s tras %s intentos",
                    incidente_id,
                    max_reintentos,
                )
        finally:
            cola.task_done()


def publicar_incidente_nuevo(resultado: ResultadoProcesamiento, bus_eventos: BusEventos) -> None:
    if not resultado.incidente_nuevo:
        return
    bus_eventos.publicar(
        AlertaIncidente(
            incidente_id=resultado.incidente_id,
            tipo_ataque=resultado.tipo_ataque,
            severidad=resultado.severidad,
            ip_origen=resultado.ip_origen,
        )
    )


async def cancelar_tarea(tarea: asyncio.Task[None] | None) -> None:
    if tarea is None:
        return
    tarea.cancel()
    with suppress(asyncio.CancelledError):
        await tarea
