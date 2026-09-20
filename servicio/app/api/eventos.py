import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.api.dependencias import UsuarioActual

router = APIRouter(tags=["eventos"])


@router.get("/eventos")
async def eventos(request: Request, usuario: UsuarioActual) -> StreamingResponse:
    del usuario

    async def flujo() -> AsyncIterator[str]:
        async with request.app.state.bus_eventos.suscribir() as cola:
            yield ": conectado\n\n"
            while not await request.is_disconnected():
                try:
                    alerta = await asyncio.wait_for(cola.get(), timeout=15)
                except TimeoutError:
                    yield ": latido\n\n"
                    continue
                try:
                    yield f"event: incidente\ndata: {json.dumps(alerta.como_dict())}\n\n"
                finally:
                    cola.task_done()

    return StreamingResponse(
        flujo(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
