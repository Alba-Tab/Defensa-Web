from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import func
from sqlmodel import col, select

from app.api.dependencias import Sesion, UsuarioActual
from app.dominio.modelos import Baneo, Incidente

router = APIRouter(prefix="/metricas", tags=["metricas"])


@router.get("")
def obtener_metricas(sesion: Sesion, usuario: UsuarioActual) -> dict[str, object]:
    del usuario
    ahora = datetime.now(UTC).replace(tzinfo=None)
    inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_ventana = (ahora - timedelta(hours=23)).replace(minute=0, second=0, microsecond=0)

    incidentes_hoy = sesion.exec(
        select(func.count()).select_from(Incidente).where(Incidente.inicio >= inicio_hoy)
    ).one()
    bloqueos_vigentes = sesion.exec(
        select(func.count())
        .select_from(Baneo)
        .where(Baneo.estado == "vigente", Baneo.expira > ahora)
    ).one()
    por_hora_db = dict(
        sesion.exec(
            select(
                func.strftime("%Y-%m-%dT%H:00:00", Incidente.inicio),
                func.count(),
            )
            .where(Incidente.inicio >= inicio_ventana)
            .group_by(func.strftime("%Y-%m-%dT%H:00:00", Incidente.inicio))
        ).all()
    )
    incidentes_por_hora = []
    for desplazamiento in range(24):
        hora = inicio_ventana + timedelta(hours=desplazamiento)
        clave = hora.strftime("%Y-%m-%dT%H:00:00")
        incidentes_por_hora.append({"hora": clave, "total": int(por_hora_db.get(clave, 0))})

    tipos = sesion.exec(
        select(Incidente.tipo_ataque, func.count())
        .group_by(Incidente.tipo_ataque)
        .order_by(func.count().desc())
    ).all()
    top_ips = sesion.exec(
        select(Incidente.ip_origen, func.count())
        .group_by(Incidente.ip_origen)
        .order_by(func.count().desc(), col(Incidente.ip_origen))
        .limit(5)
    ).all()

    return {
        "generado_en": ahora.isoformat() + "Z",
        "resumen": {
            "incidentes_hoy": int(incidentes_hoy),
            "bloqueos_vigentes": int(bloqueos_vigentes),
            "tipos_detectados": len(tipos),
        },
        "incidentes_por_hora": incidentes_por_hora,
        "tipos_ataque": [{"tipo": tipo, "total": int(total)} for tipo, total in tipos],
        "top_ips": [{"ip": ip, "total": int(total)} for ip, total in top_ips],
    }
