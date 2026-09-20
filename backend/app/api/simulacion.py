from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session

from app.api.dependencias import UsuarioActual, obtener_sesion
from app.dominio.esquemas import EventoEntrada, ResultadoProcesamiento

router = APIRouter(prefix="/simulacion", tags=["simulacion"])


@router.post(
    "/eventos",
    response_model=ResultadoProcesamiento,
    status_code=status.HTTP_201_CREATED,
)
async def simular_evento(
    entrada: EventoEntrada,
    request: Request,
    sesion: Annotated[Session, Depends(obtener_sesion)],
    usuario: UsuarioActual,
) -> ResultadoProcesamiento:
    del usuario
    if request.app.state.ajustes.modo != "simulado":
        raise HTTPException(status_code=404, detail="Ruta disponible solo en modo simulado")
    resultado: ResultadoProcesamiento = await request.app.state.procesador.procesar(entrada, sesion)
    await request.app.state.cola_enriquecimiento.put(resultado.incidente_id)
    return resultado
