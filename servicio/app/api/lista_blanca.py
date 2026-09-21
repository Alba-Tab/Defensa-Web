"""Pb-18: API de gestión de lista blanca.

Permite al administrador consultar, agregar y quitar direcciones IP o redes
de la lista blanca sin editar archivos de configuración en el servidor.
"""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.dependencias import Sesion, UsuarioActual
from app.dominio.esquemas import ListaBlancaEntrada, ListaBlancaSalida
from app.dominio.modelos import Auditoria, ListaBlanca

router = APIRouter(prefix="/lista-blanca", tags=["lista-blanca"])


@router.get("", response_model=list[ListaBlancaSalida])
def listar_lista_blanca(sesion: Sesion, usuario: UsuarioActual) -> list[ListaBlanca]:
    """Devuelve todas las entradas de la lista blanca.

    Las entradas predeterminadas (loopback, red de administración, gateway)
    se marcan con ``predeterminada=True`` y no pueden eliminarse.
    """
    del usuario
    return list(sesion.exec(select(ListaBlanca)).all())


@router.post("", response_model=ListaBlancaSalida, status_code=201)
def agregar_a_lista_blanca(
    datos: ListaBlancaEntrada,
    sesion: Sesion,
    usuario: UsuarioActual,
) -> ListaBlanca:
    """Agrega una IP o red (CIDR) a la lista blanca.

    La dirección se valida antes de guardar; un valor inválido responde 422
    sin tocar la base de datos.  No se permiten duplicados.
    """
    existente = sesion.exec(
        select(ListaBlanca).where(ListaBlanca.ip_o_red == datos.ip_o_red)
    ).first()
    if existente is not None:
        raise HTTPException(
            status_code=409,
            detail=f"'{datos.ip_o_red}' ya existe en la lista blanca",
        )

    entrada = ListaBlanca(
        ip_o_red=datos.ip_o_red,
        descripcion=datos.descripcion,
        predeterminada=False,
    )
    sesion.add(entrada)
    sesion.flush()
    sesion.add(
        Auditoria(
            actor=usuario.nombre,
            accion="lista_blanca_alta",
            ip_afectada=datos.ip_o_red,
            detalle=datos.descripcion,
        )
    )
    sesion.commit()
    sesion.refresh(entrada)
    return entrada


@router.delete("/{entrada_id}", status_code=200)
def eliminar_de_lista_blanca(
    entrada_id: int,
    sesion: Sesion,
    usuario: UsuarioActual,
) -> dict[str, str]:
    """Elimina una entrada de la lista blanca por su ``id``.

    Las entradas predeterminadas no pueden eliminarse (responde 403).
    """
    entrada = sesion.get(ListaBlanca, entrada_id)
    if entrada is None:
        raise HTTPException(status_code=404, detail="Entrada no encontrada en la lista blanca")
    if entrada.predeterminada:
        raise HTTPException(
            status_code=403,
            detail="Las entradas predeterminadas no pueden eliminarse",
        )

    ip_afectada = entrada.ip_o_red
    sesion.delete(entrada)
    sesion.add(
        Auditoria(
            actor=usuario.nombre,
            accion="lista_blanca_baja",
            ip_afectada=ip_afectada,
        )
    )
    sesion.commit()
    return {"estado": "eliminado", "ip_o_red": ip_afectada}
