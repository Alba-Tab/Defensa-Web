from fastapi import APIRouter, Request

from app.api.dependencias import UsuarioActual

router = APIRouter(tags=["operacion"])


@router.get("/salud")
def salud(request: Request, usuario: UsuarioActual) -> dict[str, str]:
    del usuario
    estado_suricata: str = request.app.state.monitor_suricata.estado()
    return {
        "estado": "degradado" if estado_suricata == "inactivo" else "operativo",
        "modo": request.app.state.ajustes.modo,
        "entorno": request.app.state.ajustes.entorno,
        "suricata": estado_suricata,
        "fuente_eventos": type(request.app.state.fuente).__name__,
        "actuador": type(request.app.state.actuador).__name__,
        "clasificador": type(request.app.state.clasificador).__name__,
        "notificador": type(request.app.state.notificador).__name__,
    }
