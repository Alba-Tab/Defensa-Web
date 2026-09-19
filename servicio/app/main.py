from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.salud import router as router_salud
from app.api.simulacion import router as router_simulacion
from app.componentes.actuador import DryRunActuator
from app.componentes.correlador import Correlador
from app.componentes.politicas import MotorPoliticas
from app.config import Ajustes, obtener_ajustes
from app.database import crear_motor
from app.servicios import ProcesadorEventos


def crear_aplicacion(ajustes: Ajustes | None = None) -> FastAPI:
    configuracion = ajustes or obtener_ajustes()
    motor = crear_motor(configuracion)
    actuador = DryRunActuator()
    correlador = Correlador(configuracion.ventana_correlacion_segundos)
    politicas = MotorPoliticas(
        actuador,
        umbral_eventos=configuracion.umbral_eventos,
        ventana_segundos=configuracion.ventana_bloqueo_segundos,
        duracion_segundos=configuracion.duracion_bloqueo_segundos,
        lista_blanca=configuracion.lista_blanca,
    )
    procesador = ProcesadorEventos(correlador, politicas)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.ajustes = configuracion
        app.state.motor = motor
        app.state.actuador = actuador
        app.state.procesador = procesador
        yield
        motor.dispose()

    aplicacion = FastAPI(
        title="Plataforma de Defensa Web",
        version="0.1.0",
        lifespan=lifespan,
    )
    aplicacion.include_router(router_salud, prefix="/api")
    aplicacion.include_router(router_simulacion, prefix="/api")
    return aplicacion


app = crear_aplicacion()
