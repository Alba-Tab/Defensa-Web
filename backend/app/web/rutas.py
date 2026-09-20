from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.web import DIRECTORIO_PLANTILLAS

router = APIRouter(include_in_schema=False)
plantillas = Jinja2Templates(directory=DIRECTORIO_PLANTILLAS)


@router.get("/", response_class=HTMLResponse)
async def mostrar_panel(request: Request) -> HTMLResponse:
    return plantillas.TemplateResponse(
        request=request,
        name="panel.html",
        context={"titulo": "Panel de defensa"},
    )
