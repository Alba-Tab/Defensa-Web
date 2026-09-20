from collections.abc import Iterator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.database import proveedor_sesion
from app.dominio.modelos import Usuario

portador = HTTPBearer(auto_error=False)
NOMBRE_COOKIE_SESION = "defensa_sesion"


def obtener_sesion(request: Request) -> Iterator[Session]:
    yield from proveedor_sesion(request.app.state.motor)


def token_de_peticion(
    request: Request,
    credenciales: HTTPAuthorizationCredentials | None = None,
) -> str | None:
    if credenciales is not None:
        return credenciales.credentials
    autorizacion = request.headers.get("authorization", "")
    if autorizacion.lower().startswith("bearer "):
        return autorizacion[7:].strip()
    return request.cookies.get(NOMBRE_COOKIE_SESION)


def usuario_actual(
    request: Request,
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(portador)],
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> Usuario:
    excepcion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o vencidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = token_de_peticion(request, credenciales)
    if token is None:
        raise excepcion
    try:
        contenido = request.app.state.tokens.decodificar(token)
        usuario_id = int(str(contenido["sub"]))
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
        raise excepcion from error
    usuario = sesion.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise excepcion
    return usuario


def usuario_opcional(
    request: Request,
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(portador)],
    sesion: Annotated[Session, Depends(obtener_sesion)],
) -> Usuario | None:
    token = token_de_peticion(request, credenciales)
    if token is None:
        return None
    try:
        contenido = request.app.state.tokens.decodificar(token)
        usuario_id = int(str(contenido["sub"]))
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        return None
    usuario = sesion.get(Usuario, usuario_id)
    return usuario if usuario is not None and usuario.activo else None


Sesion = Annotated[Session, Depends(obtener_sesion)]
UsuarioActual = Annotated[Usuario, Depends(usuario_actual)]
UsuarioOpcional = Annotated[Usuario | None, Depends(usuario_opcional)]
