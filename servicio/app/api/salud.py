from fastapi import APIRouter, Request

router = APIRouter(tags=["operacion"])


@router.get("/salud")
def salud(request: Request) -> dict[str, str]:
    return {
        "estado": "operativo",
        "modo": request.app.state.ajustes.modo,
        "entorno": request.app.state.ajustes.entorno,
    }
