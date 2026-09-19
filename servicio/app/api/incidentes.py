from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, select

from app.api.dependencias import Sesion, UsuarioActual
from app.dominio.esquemas import IncidenteSalida
from app.dominio.modelos import Incidente

router = APIRouter(prefix="/incidentes", tags=["incidentes"])


@router.get("", response_model=list[IncidenteSalida])
def listar_incidentes(
    sesion: Sesion,
    usuario: UsuarioActual,
    limite: Annotated[int, Query(ge=1, le=100)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> list[Incidente]:
    del usuario
    return list(
        sesion.exec(
            select(Incidente)
            .order_by(col(Incidente.ultima_actividad).desc())
            .offset(desplazamiento)
            .limit(limite)
        ).all()
    )


@router.get("/{incidente_id}", response_model=IncidenteSalida)
def obtener_incidente(incidente_id: int, sesion: Sesion, usuario: UsuarioActual) -> Incidente:
    del usuario
    incidente = sesion.get(Incidente, incidente_id)
    if incidente is None:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incidente
