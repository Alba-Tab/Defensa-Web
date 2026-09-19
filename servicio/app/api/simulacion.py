from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session

from app.database import proveedor_sesion
from app.dominio.esquemas import EventoEntrada, ResultadoProcesamiento

router = APIRouter(prefix="/simulacion", tags=["simulacion"])


def obtener_sesion(request: Request) -> Iterator[Session]:
    yield from proveedor_sesion(request.app.state.motor)


@router.post(
    "/eventos",
    response_model=ResultadoProcesamiento,
    status_code=status.HTTP_201_CREATED,
)
async def simular_evento(
    entrada: EventoEntrada,
    request: Request,
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> ResultadoProcesamiento:
    if request.app.state.ajustes.modo != "simulado":
        raise HTTPException(status_code=404, detail="Ruta disponible solo en modo simulado")
    return await request.app.state.procesador.procesar(entrada, sesion)
