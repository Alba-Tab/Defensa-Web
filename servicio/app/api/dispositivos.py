from datetime import UTC, datetime

from fastapi import APIRouter, status
from sqlmodel import select

from app.api.dependencias import Sesion, UsuarioActual
from app.dominio.esquemas import DispositivoEntrada
from app.dominio.modelos import Dispositivo

router = APIRouter(prefix="/dispositivos", tags=["dispositivos"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def registrar_dispositivo(
    entrada: DispositivoEntrada, sesion: Sesion, usuario: UsuarioActual
) -> None:
    dispositivo = sesion.exec(
        select(Dispositivo).where(Dispositivo.token_fcm == entrada.token_fcm)
    ).first()
    ahora = datetime.now(UTC).replace(tzinfo=None)
    if dispositivo is None:
        dispositivo = Dispositivo(
            token_fcm=entrada.token_fcm,
            plataforma=entrada.plataforma,
            usuario_id=usuario.id,
            alta=ahora,
            actualizado_en=ahora,
        )
    else:
        dispositivo.plataforma = entrada.plataforma
        dispositivo.usuario_id = usuario.id
        dispositivo.actualizado_en = ahora
        dispositivo.activo = True
    sesion.add(dispositivo)
    sesion.commit()
