import asyncio
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select

from app.api.auth import router as router_auth
from app.api.baneos import router as router_baneos
from app.api.dispositivos import router as router_dispositivos
from app.api.incidentes import router as router_incidentes
from app.api.salud import router as router_salud
from app.api.simulacion import router as router_simulacion
from app.componentes.actuador import ActuadorBloqueo, DryRunActuator, Fail2banActuator
from app.componentes.clasificador import Clasificador, ClasificadorJoblib, ClasificadorNulo
from app.componentes.correlador import Correlador
from app.componentes.fuente_eventos import EveSource, FakeSource, FuenteEventos
from app.componentes.informes import GeneradorInformes, GeneradorOpenRouter, GeneradorPlantilla
from app.componentes.notificador import Notificador, NotificadorFirebase, NotificadorNulo
from app.componentes.politicas import MotorPoliticas
from app.config import Ajustes, obtener_ajustes
from app.database import crear_motor
from app.dominio.modelos import Usuario
from app.integracion import cancelar_tarea, consumir_eventos, enriquecer_incidentes
from app.seguridad import LimitadorLogin, ServicioContrasenas, ServicioTokens
from app.servicios import ProcesadorEventos


def crear_aplicacion(ajustes: Ajustes | None = None) -> FastAPI:
    configuracion = ajustes or obtener_ajustes()
    motor = crear_motor(configuracion)
    fuente: FuenteEventos
    actuador: ActuadorBloqueo
    if configuracion.modo == "real":
        fuente = EveSource(configuracion.eve_json)
        actuador = Fail2banActuator(configuracion.fail2ban_binario, configuracion.fail2ban_jail)
    else:
        fuente = FakeSource()
        actuador = DryRunActuator()

    clasificador: Clasificador
    if configuracion.modelo_clasificador and configuracion.modelo_clasificador.exists():
        clasificador = ClasificadorJoblib(
            configuracion.modelo_clasificador, configuracion.umbral_confianza
        )
    else:
        clasificador = ClasificadorNulo()

    generador: GeneradorInformes
    if configuracion.openrouter_api_key and configuracion.openrouter_modelo:
        generador = GeneradorOpenRouter(
            configuracion.openrouter_url,
            configuracion.openrouter_api_key.get_secret_value(),
            configuracion.openrouter_modelo,
            configuracion.timeout_ia_segundos,
            configuracion.openrouter_referer,
        )
    else:
        generador = GeneradorPlantilla()

    notificador: Notificador = (
        NotificadorFirebase(configuracion.fcm_credenciales)
        if configuracion.fcm_credenciales and configuracion.fcm_credenciales.exists()
        else NotificadorNulo()
    )
    correlador = Correlador(configuracion.ventana_correlacion_segundos)
    politicas = MotorPoliticas(
        actuador,
        umbral_eventos=configuracion.umbral_eventos,
        ventana_segundos=configuracion.ventana_bloqueo_segundos,
        duracion_segundos=configuracion.duracion_bloqueo_segundos,
        lista_blanca=configuracion.lista_blanca,
    )
    procesador = ProcesadorEventos(correlador, politicas, clasificador)
    contrasenas = ServicioContrasenas()
    secreto = (
        configuracion.jwt_secret.get_secret_value()
        if configuracion.jwt_secret
        else secrets.token_urlsafe(48)
    )
    tokens = ServicioTokens(secreto, configuracion.token_minutos)
    limitador_login = LimitadorLogin()
    cola_enriquecimiento: asyncio.Queue[int] = asyncio.Queue(maxsize=1000)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.ajustes = configuracion
        app.state.motor = motor
        app.state.fuente = fuente
        app.state.actuador = actuador
        app.state.clasificador = clasificador
        app.state.notificador = notificador
        app.state.procesador = procesador
        app.state.contrasenas = contrasenas
        app.state.tokens = tokens
        app.state.limitador_login = limitador_login
        app.state.cola_enriquecimiento = cola_enriquecimiento

        if configuracion.admin_password:
            with Session(motor) as sesion:
                usuario = sesion.exec(
                    select(Usuario).where(Usuario.nombre == configuracion.admin_usuario)
                ).first()
                if usuario is None:
                    sesion.add(
                        Usuario(
                            nombre=configuracion.admin_usuario,
                            hash_contrasena=contrasenas.crear_hash(
                                configuracion.admin_password.get_secret_value()
                            ),
                        )
                    )
                    sesion.commit()

        tarea_enriquecimiento = asyncio.create_task(
            enriquecer_incidentes(cola_enriquecimiento, motor, generador, notificador),
            name="enriquecer-incidentes",
        )
        tarea_ingesta = (
            asyncio.create_task(
                consumir_eventos(fuente, procesador, motor, cola_enriquecimiento),
                name="consumir-eve",
            )
            if configuracion.modo == "real"
            else None
        )
        yield
        await cancelar_tarea(tarea_ingesta)
        await cancelar_tarea(tarea_enriquecimiento)
        motor.dispose()

    aplicacion = FastAPI(
        title="Plataforma de Defensa Web",
        version="0.2.0",
        lifespan=lifespan,
    )
    aplicacion.include_router(router_auth, prefix="/api")
    aplicacion.include_router(router_salud, prefix="/api")
    aplicacion.include_router(router_simulacion, prefix="/api")
    aplicacion.include_router(router_incidentes, prefix="/api")
    aplicacion.include_router(router_baneos, prefix="/api")
    aplicacion.include_router(router_dispositivos, prefix="/api")
    return aplicacion


app = crear_aplicacion()
