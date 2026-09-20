from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.api.dependencias import UsuarioOpcional
from app.web import DIRECTORIO_PLANTILLAS

router = APIRouter(include_in_schema=False)
plantillas = Jinja2Templates(directory=DIRECTORIO_PLANTILLAS)


@router.get("/", response_class=HTMLResponse)
async def mostrar_panel(request: Request, usuario: UsuarioOpcional) -> Response:
    if usuario is None:
        return RedirectResponse(url="/login", status_code=303)
    return plantillas.TemplateResponse(
        request=request,
        name="panel.html",
        context={"titulo": "Panel de defensa", "usuario": usuario},
    )


@router.get("/login", response_class=HTMLResponse)
async def mostrar_login(request: Request, usuario: UsuarioOpcional) -> Response:
    if usuario is not None:
        return RedirectResponse(url="/", status_code=303)
    return plantillas.TemplateResponse(
        request=request,
        name="login.html",
        context={"titulo": "Iniciar sesión"},
    )
