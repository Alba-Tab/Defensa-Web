from datetime import UTC, datetime
from ipaddress import ip_address
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
    desde: str | None = None,
    hasta: str | None = None,
    ip_origen: str | None = None,
    severidad: str | None = None,
    limite: Annotated[int, Query(ge=1, le=100)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> list[Incidente]:
    del usuario
    fecha_desde = _fecha_consulta(desde, "desde")
    fecha_hasta = _fecha_consulta(hasta, "hasta")
    if fecha_desde is not None and fecha_hasta is not None and fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=400,
            detail="El valor de desde no puede ser posterior a hasta",
        )

    ip_canonica: str | None = None
    if ip_origen is not None:
        try:
            ip_canonica = str(ip_address(ip_origen))
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail="Dirección IP de origen inválida",
            ) from error

    severidad_numerica: int | None = None
    if severidad is not None:
        try:
            severidad_numerica = int(severidad)
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail="La severidad debe ser un número entero",
            ) from error
        if severidad_numerica not in (1, 2, 3, 4):
            raise HTTPException(status_code=400, detail="La severidad debe estar entre 1 y 4")

    sentencia = select(Incidente)
    if fecha_desde is not None:
        sentencia = sentencia.where(Incidente.ultima_actividad >= fecha_desde)
    if fecha_hasta is not None:
        sentencia = sentencia.where(Incidente.ultima_actividad <= fecha_hasta)
    if ip_canonica is not None:
        sentencia = sentencia.where(Incidente.ip_origen == ip_canonica)
    if severidad_numerica is not None:
        sentencia = sentencia.where(Incidente.severidad == severidad_numerica)

    return list(
        sesion.exec(
            sentencia.order_by(col(Incidente.ultima_actividad).desc())
            .offset(desplazamiento)
            .limit(limite)
        ).all()
    )


def _fecha_consulta(valor: str | None, nombre: str) -> datetime | None:
    if valor is None:
        return None
    try:
        fecha = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=f"Fecha inválida en {nombre}") from error
    if fecha.tzinfo is not None:
        fecha = fecha.astimezone(UTC).replace(tzinfo=None)
    return fecha


@router.get("/{incidente_id}", response_model=IncidenteSalida)
def obtener_incidente(incidente_id: int, sesion: Sesion, usuario: UsuarioActual) -> Incidente:
    del usuario
    incidente = sesion.get(Incidente, incidente_id)
    if incidente is None:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incidente
