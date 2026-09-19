import asyncio
import logging
from contextlib import suppress

from sqlalchemy import Engine
from sqlmodel import Session, col, select

from app.componentes.fuente_eventos import FuenteEventos
from app.componentes.informes import GeneradorInformes
from app.componentes.notificador import Notificador
from app.dominio.modelos import Dispositivo, Incidente
from app.servicios import ProcesadorEventos

logger = logging.getLogger(__name__)


async def consumir_eventos(
    fuente: FuenteEventos,
    procesador: ProcesadorEventos,
    motor: Engine,
    cola_enriquecimiento: asyncio.Queue[int],
) -> None:
    async for evento in fuente.eventos():
        try:
            with Session(motor) as sesion:
                resultado = await procesador.procesar(evento, sesion)
            if resultado.incidente_nuevo:
                await cola_enriquecimiento.put(resultado.incidente_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("No se pudo procesar un evento de eve.json")
            continue


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
) -> None:
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
                sesion.expunge(incidente)

            informe, origen = await generador.generar(incidente)
            with Session(motor) as sesion:
                persistido = sesion.get(Incidente, incidente_id)
                if persistido is None:
                    continue
                persistido.categoria_owasp = incidente.categoria_owasp
                persistido.informe = informe
                persistido.origen_informe = origen
                sesion.add(persistido)
                sesion.commit()
                sesion.refresh(persistido)

                if persistido.severidad <= 1:
                    dispositivos = sesion.exec(
                        select(Dispositivo).where(col(Dispositivo.activo).is_(True))
                    ).all()
                    invalidos = await notificador.enviar(
                        persistido, [dispositivo.token_fcm for dispositivo in dispositivos]
                    )
                    for dispositivo in dispositivos:
                        if dispositivo.token_fcm in invalidos:
                            dispositivo.activo = False
                            sesion.add(dispositivo)
                    sesion.commit()
        finally:
            cola.task_done()


async def cancelar_tarea(tarea: asyncio.Task[None] | None) -> None:
    if tarea is None:
        return
    tarea.cancel()
    with suppress(asyncio.CancelledError):
        await tarea
