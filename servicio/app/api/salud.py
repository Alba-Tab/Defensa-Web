import httpx
from fastapi import APIRouter, Request

from app.api.dependencias import UsuarioActual
from app.componentes.estado_componentes import MonitorSuricataSystemd

router = APIRouter(tags=["operacion"])


@router.get("/salud")
def salud(request: Request, usuario: UsuarioActual) -> dict[str, str]:
    del usuario
    estado_suricata: str = request.app.state.monitor_suricata.estado()
    if request.app.state.ajustes.modo == "real":
        estado_nginx = _estado_systemd(request, request.app.state.ajustes.nginx_servicio)
        estado_fail2ban = _estado_systemd(request, request.app.state.ajustes.fail2ban_servicio)
    else:
        estado_nginx = "no_aplica"
        estado_fail2ban = "no_aplica"
    estado_ollama = _estado_ollama(request)
    componentes = {
        "nginx": estado_nginx,
        "suricata": estado_suricata,
        "fail2ban": estado_fail2ban,
        "ollama": estado_ollama,
    }
    return {
        "estado": "degradado" if "inactivo" in componentes.values() else "operativo",
        "modo": request.app.state.ajustes.modo,
        "entorno": request.app.state.ajustes.entorno,
        **componentes,
        "fuente_eventos": type(request.app.state.fuente).__name__,
        "actuador": type(request.app.state.actuador).__name__,
        "clasificador": type(request.app.state.clasificador).__name__,
        "notificador": type(request.app.state.notificador).__name__,
    }


def _estado_systemd(request: Request, servicio: str) -> str:
    monitor = MonitorSuricataSystemd(
        request.app.state.ajustes.systemctl_binario,
        servicio,
        request.app.state.ajustes.salud_timeout_segundos,
    )
    return monitor.estado()


def _estado_ollama(request: Request) -> str:
    url = request.app.state.ajustes.ollama_url
    if not url:
        return "no_configurado"
    try:
        respuesta = httpx.get(
            f"{url.rstrip('/')}/api/tags",
            timeout=request.app.state.ajustes.salud_timeout_segundos,
        )
        return "activo" if respuesta.is_success else "inactivo"
    except httpx.HTTPError:
        return "inactivo"
