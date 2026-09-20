from collections.abc import Iterator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.database import proveedor_sesion
from app.dominio.modelos import Usuario

portador = HTTPBearer(auto_error=False)


def obtener_sesion(request: Request) -> Iterator[Session]:
    yield from proveedor_sesion(request.app.state.motor)


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
    if credenciales is None:
        raise excepcion
    try:
        contenido = request.app.state.tokens.decodificar(credenciales.credentials)
        usuario_id = int(str(contenido["sub"]))
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
        raise excepcion from error
    usuario = sesion.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise excepcion
    return usuario


Sesion = Annotated[Session, Depends(obtener_sesion)]
UsuarioActual = Annotated[Usuario, Depends(usuario_actual)]
