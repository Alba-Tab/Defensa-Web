from sqlmodel import Session

from app.componentes.correlador import Correlador
from app.componentes.politicas import MotorPoliticas
from app.dominio.esquemas import EventoEntrada, ResultadoProcesamiento


class ProcesadorEventos:
    def __init__(self, correlador: Correlador, politicas: MotorPoliticas) -> None:
        self._correlador = correlador
        self._politicas = politicas

    async def procesar(self, entrada: EventoEntrada, sesion: Session) -> ResultadoProcesamiento:
        try:
            incidente, evento = self._correlador.registrar(entrada, sesion)
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
            )
        except Exception:
            sesion.rollback()
            raise
