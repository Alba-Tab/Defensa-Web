from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request
from sqlmodel import select

from app.api.dependencias import Sesion
from app.dominio.esquemas import CredencialesEntrada, TokenSalida
from app.dominio.modelos import Usuario

router = APIRouter(prefix="/auth", tags=["autenticacion"])


@router.post("/login", response_model=TokenSalida)
def iniciar_sesion(
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
    return TokenSalida(
        access_token=request.app.state.tokens.crear(usuario.id, usuario.nombre),
        expires_in=request.app.state.tokens.duracion_segundos,
    )
