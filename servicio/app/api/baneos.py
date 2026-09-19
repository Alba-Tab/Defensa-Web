from datetime import UTC, datetime
from ipaddress import ip_address

from fastapi import APIRouter, HTTPException, Request
from sqlmodel import col, select

from app.api.dependencias import Sesion, UsuarioActual
from app.dominio.esquemas import BaneoSalida
from app.dominio.modelos import Auditoria, Baneo

router = APIRouter(prefix="/baneos", tags=["baneos"])


@router.get("", response_model=list[BaneoSalida])
def listar_baneos(sesion: Sesion, usuario: UsuarioActual) -> list[Baneo]:
    del usuario
    return list(sesion.exec(select(Baneo).order_by(col(Baneo.inicio).desc())).all())


@router.post("/{ip}/liberar")
async def liberar_baneo(
    ip: str,
    request: Request,
    sesion: Sesion,
    usuario: UsuarioActual,
) -> dict[str, str]:
    try:
        ip_canonica = str(ip_address(ip))
    except ValueError as error:
        raise HTTPException(status_code=422, detail="Dirección IP inválida") from error

    vigentes = sesion.exec(
        select(Baneo).where(Baneo.ip == ip_canonica, Baneo.estado == "vigente")
    ).all()
    await request.app.state.actuador.liberar(ip_canonica)
    for baneo in vigentes:
        baneo.estado = "liberado"
        sesion.add(baneo)
    sesion.add(
        Auditoria(
            fecha_utc=datetime.now(UTC).replace(tzinfo=None),
            actor=usuario.nombre,
            accion="liberacion_manual",
            ip_afectada=ip_canonica,
        )
    )
    sesion.commit()
    return {"estado": "liberado", "ip": ip_canonica}
