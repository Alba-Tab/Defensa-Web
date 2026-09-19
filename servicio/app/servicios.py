from sqlmodel import Session

from app.componentes.clasificador import Clasificador
from app.componentes.correlador import Correlador
from app.componentes.politicas import MotorPoliticas
from app.dominio.esquemas import EventoEntrada, ResultadoProcesamiento


class ProcesadorEventos:
    def __init__(
        self, correlador: Correlador, politicas: MotorPoliticas, clasificador: Clasificador
    ) -> None:
        self._correlador = correlador
        self._politicas = politicas
        self._clasificador = clasificador

    async def procesar(self, entrada: EventoEntrada, sesion: Session) -> ResultadoProcesamiento:
        try:
            incidente, evento, nuevo = self._correlador.registrar(entrada, sesion)
            clasificacion = await self._clasificador.clasificar(entrada)
            incidente.confianza_clasificador = clasificacion.confianza
            if clasificacion.tipo != "indeterminado":
                incidente.tipo_ataque = clasificacion.tipo
            if clasificacion.severidad is not None:
                incidente.severidad = min(incidente.severidad, clasificacion.severidad)
            baneo = await self._politicas.evaluar(incidente, entrada.fecha_utc, sesion)
            sesion.commit()
            sesion.refresh(incidente)
            sesion.refresh(evento)
            if baneo is not None:
                sesion.refresh(baneo)
            assert incidente.id is not None
            assert evento.id is not None
            return ResultadoProcesamiento(
                incidente_id=incidente.id,
                evento_id=evento.id,
                baneo_id=baneo.id if baneo else None,
                incidente_nuevo=nuevo,
            )
        except Exception:
            sesion.rollback()
            raise
