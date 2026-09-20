from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlmodel import select

from app.api.dependencias import NOMBRE_COOKIE_SESION, Sesion
from app.dominio.esquemas import CredencialesEntrada, TokenSalida
from app.dominio.modelos import Usuario

router = APIRouter(prefix="/auth", tags=["autenticacion"])


@router.post("/login", response_model=TokenSalida)
def iniciar_sesion(
    entrada: CredencialesEntrada,
    request: Request,
    sesion: Sesion,
) -> TokenSalida:
    return _autenticar(entrada, request, sesion)


@router.post("/sesion", response_model=TokenSalida)
def iniciar_sesion_web(
    entrada: CredencialesEntrada,
    request: Request,
    response: Response,
    sesion: Sesion,
) -> TokenSalida:
    salida = _autenticar(entrada, request, sesion)
    response.set_cookie(
        key=NOMBRE_COOKIE_SESION,
        value=salida.access_token,
        max_age=salida.expires_in,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        path="/",
    )
    return salida


def _autenticar(
    entrada: CredencialesEntrada,
    request: Request,
    sesion: Sesion,
) -> TokenSalida:
    ip = request.client.host if request.client else "desconocida"
    ahora = datetime.now(UTC)
    if request.app.state.limitador_login.bloqueado(ip, ahora):
        raise HTTPException(status_code=429, detail="Demasiados intentos; inténtelo más tarde")

    usuario = sesion.exec(select(Usuario).where(Usuario.nombre == entrada.usuario)).first()
    valido = usuario is not None and request.app.state.contrasenas.verificar(
        usuario.hash_contrasena, entrada.contrasena
    )
    if not valido or usuario is None or not usuario.activo:
        request.app.state.limitador_login.registrar_fallo(ip, ahora)
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    request.app.state.limitador_login.limpiar(ip)
    assert usuario.id is not None
    token = request.app.state.tokens.crear(usuario.id, usuario.nombre)
    return TokenSalida(access_token=token, expires_in=request.app.state.tokens.duracion_segundos)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion(response: Response) -> None:
    response.delete_cookie(NOMBRE_COOKIE_SESION, path="/", samesite="strict")
