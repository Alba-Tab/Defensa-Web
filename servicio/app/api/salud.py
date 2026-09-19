from fastapi import APIRouter, Request

router = APIRouter(tags=["operacion"])


@router.get("/salud")
def salud(request: Request) -> dict[str, str]:
    return {
        "estado": "operativo",
        "modo": request.app.state.ajustes.modo,
        "entorno": request.app.state.ajustes.entorno,
        "fuente_eventos": type(request.app.state.fuente).__name__,
        "actuador": type(request.app.state.actuador).__name__,
        "clasificador": type(request.app.state.clasificador).__name__,
        "notificador": type(request.app.state.notificador).__name__,
    }
