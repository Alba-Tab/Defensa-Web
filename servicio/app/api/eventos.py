import asyncio
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import jwt
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import Engine
from sqlmodel import Session, col, select

from app.api.dependencias import UsuarioActual, token_de_peticion
from app.componentes.eventos_tiempo_real import AlertaIncidente
from app.dominio.modelos import Incidente

router = APIRouter(tags=["eventos"])


@router.get("/eventos")
async def eventos(
    request: Request,
    usuario: UsuarioActual,
    ultimo_id: int | None = None,
) -> StreamingResponse:
    del usuario
    token = token_de_peticion(request)
    assert token is not None
    try:
        contenido = request.app.state.tokens.decodificar(token)
        expira_en = float(contenido["exp"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        expira_en = 0

    encabezado_id = request.headers.get("last-event-id")
    if encabezado_id is not None:
        try:
            ultimo_id = int(encabezado_id)
        except ValueError:
            ultimo_id = None

    async def flujo() -> AsyncIterator[str]:
        async with request.app.state.bus_eventos.suscribir() as cola:
            yield ": conectado\n\n"
            if ultimo_id is not None:
                for alerta in _alertas_posteriores(request.app.state.motor, ultimo_id):
                    yield _serializar_alerta(alerta)
            while not await request.is_disconnected():
                restante = expira_en - datetime.now(UTC).timestamp()
                if restante <= 0:
                    yield "event: sesion_expirada\ndata: {}\n\n"
                    break
                try:
                    alerta = await asyncio.wait_for(cola.get(), timeout=min(15, restante))
                except TimeoutError:
                    yield ": latido\n\n"
                    continue
                try:
                    yield _serializar_alerta(alerta)
                finally:
                    cola.task_done()

    return StreamingResponse(
        flujo(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _serializar_alerta(alerta: AlertaIncidente) -> str:
    return (
        f"id: {alerta.incidente_id}\nevent: incidente\ndata: {json.dumps(alerta.como_dict())}\n\n"
    )


def _alertas_posteriores(motor: Engine, ultimo_id: int) -> list[AlertaIncidente]:
    with Session(motor) as sesion:
        incidentes = sesion.exec(
            select(Incidente).where(col(Incidente.id) > ultimo_id).order_by(col(Incidente.id))
        ).all()
        return [
            AlertaIncidente(
                incidente_id=incidente.id,
                tipo_ataque=incidente.tipo_ataque,
                severidad=incidente.severidad,
                ip_origen=incidente.ip_origen,
            )
            for incidente in incidentes
            if incidente.id is not None
        ]
