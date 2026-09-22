import asyncio
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app.api.auth import router as router_auth
from app.api.baneos import router as router_baneos
from app.api.dispositivos import router as router_dispositivos
from app.api.eventos import router as router_eventos
from app.api.incidentes import router as router_incidentes
from app.api.lista_blanca import router as router_lista_blanca
from app.api.metricas import router as router_metricas
from app.api.salud import router as router_salud
from app.api.simulacion import router as router_simulacion
from app.componentes.actuador import ActuadorBloqueo, DryRunActuator, Fail2banActuator
from app.componentes.clasificador import Clasificador, ClasificadorJoblib, ClasificadorNulo
from app.componentes.conciliador import Conciliador
from app.componentes.correlador import Correlador
from app.componentes.detector_fuerza_bruta import DetectorFuerzaBruta
from app.componentes.estado_componentes import (
    MonitorSuricata,
    MonitorSuricataSimulado,
    MonitorSuricataSystemd,
)
from app.componentes.eventos_tiempo_real import BusEventos
from app.componentes.fuente_eventos import EveSource, FakeSource, FuenteEventos
from app.componentes.informes import GeneradorInformes, GeneradorOllama, GeneradorPlantilla
from app.componentes.notificador import Notificador, NotificadorFirebase, NotificadorNulo
from app.componentes.politicas import MotorPoliticas
from app.config import Ajustes, obtener_ajustes
from app.database import crear_motor
from app.dominio.modelos import ListaBlanca, Usuario
from app.integracion import (
    cancelar_tarea,
    consumir_eventos,
    enriquecer_incidentes,
    mantener_estado,
    procesar_fuerza_bruta,
)
from app.repositorio import Repositorio
from app.seguridad import LimitadorLogin, ServicioContrasenas, ServicioTokens
from app.servicios import ProcesadorEventos
from app.web import DIRECTORIO_ESTATICO
from app.web.rutas import router as router_panel


def crear_aplicacion(ajustes: Ajustes | None = None) -> FastAPI:
    configuracion = ajustes or obtener_ajustes()
    motor = crear_motor(configuracion)
    fuente: FuenteEventos
    actuador: ActuadorBloqueo
    monitor_suricata: MonitorSuricata
    if configuracion.modo == "real":
        fuente = EveSource(configuracion.eve_json)
        actuador = Fail2banActuator(configuracion.fail2ban_binario, configuracion.fail2ban_jail)
        monitor_suricata = MonitorSuricataSystemd(
            configuracion.systemctl_binario,
            configuracion.suricata_servicio,
            configuracion.salud_timeout_segundos,
        )
    else:
        fuente = FakeSource()
        actuador = DryRunActuator()
        monitor_suricata = MonitorSuricataSimulado()

    clasificador: Clasificador
    if configuracion.modelo_clasificador and configuracion.modelo_clasificador.exists():
        clasificador = ClasificadorJoblib(
            configuracion.modelo_clasificador, configuracion.umbral_confianza
        )
    else:
        clasificador = ClasificadorNulo()

    generador = crear_generador_informes(configuracion)

    notificador: Notificador = (
        NotificadorFirebase(configuracion.fcm_credenciales)
        if configuracion.fcm_credenciales and configuracion.fcm_credenciales.exists()
        else NotificadorNulo()
    )
    correlador = Correlador(configuracion.ventana_correlacion_segundos)
    bus_eventos = BusEventos()
    politicas = MotorPoliticas(
        actuador,
        umbral_eventos=configuracion.umbral_eventos,
        ventana_segundos=configuracion.ventana_bloqueo_segundos,
        duracion_segundos=configuracion.duracion_bloqueo_segundos,
        lista_blanca=configuracion.lista_blanca,
    )
    procesador = ProcesadorEventos(correlador, politicas, clasificador)
    repositorio = Repositorio(motor, configuracion.ventana_correlacion_segundos)
    conciliador = Conciliador(repositorio, actuador)
    contrasenas = ServicioContrasenas()
    secreto = (
        configuracion.jwt_secret.get_secret_value()
        if configuracion.jwt_secret
        else secrets.token_urlsafe(48)
    )
    tokens = ServicioTokens(secreto, configuracion.token_minutos)
    limitador_login = LimitadorLogin(
        max_intentos=configuracion.login_max_intentos,
        ventana_segundos=configuracion.login_ventana_segundos,
        bloqueo_segundos=configuracion.login_bloqueo_segundos,
    )
    detector_fuerza_bruta = DetectorFuerzaBruta(
        configuracion.nginx_access_log,
        configuracion.brute_force_umbral,
        configuracion.brute_force_ventana_segundos,
    )
    cola_enriquecimiento: asyncio.Queue[int] = asyncio.Queue(maxsize=1000)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.ajustes = configuracion
        app.state.motor = motor
        app.state.fuente = fuente
        app.state.monitor_suricata = monitor_suricata
        app.state.actuador = actuador
        app.state.clasificador = clasificador
        app.state.generador = generador
        app.state.notificador = notificador
        app.state.procesador = procesador
        app.state.repositorio = repositorio
        app.state.conciliador = conciliador
        app.state.contrasenas = contrasenas
        app.state.tokens = tokens
        app.state.limitador_login = limitador_login
        app.state.cola_enriquecimiento = cola_enriquecimiento
        app.state.bus_eventos = bus_eventos
        app.state.detector_fuerza_bruta = detector_fuerza_bruta

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

        # Pb-18: sembrar entradas predeterminadas en la lista blanca si no existen
        _sembrar_lista_blanca(motor, configuracion.lista_blanca)

        resultado_conciliacion = await conciliador.ejecutar()
        app.state.resultado_conciliacion = resultado_conciliacion

        tarea_enriquecimiento = asyncio.create_task(
            enriquecer_incidentes(
                cola_enriquecimiento,
                motor,
                generador,
                notificador,
            ),
            name="enriquecer-incidentes",
        )
        tarea_ingesta = (
            asyncio.create_task(
                consumir_eventos(fuente, procesador, motor, cola_enriquecimiento, bus_eventos),
                name="consumir-eve",
            )
            if configuracion.modo == "real"
            else None
        )
        tarea_mantenimiento = asyncio.create_task(
            mantener_estado(
                repositorio,
                conciliador,
                cola_enriquecimiento,
                configuracion.intervalo_mantenimiento_segundos,
            ),
            name="mantener-incidentes",
        )
        tarea_fuerza_bruta = (
            asyncio.create_task(
                procesar_fuerza_bruta(
                    detector_fuerza_bruta,
                    procesador,
                    motor,
                    cola_enriquecimiento,
                    bus_eventos,
                ),
                name="detectar-fuerza-bruta",
            )
            if configuracion.modo == "real"
            else None
        )
        yield
        await cancelar_tarea(tarea_ingesta)
        await cancelar_tarea(tarea_mantenimiento)
        await cancelar_tarea(tarea_fuerza_bruta)
        await cancelar_tarea(tarea_enriquecimiento)
        motor.dispose()

    aplicacion = FastAPI(
        title="Plataforma de Defensa Web",
        version="0.2.0",
        lifespan=lifespan,
    )
    aplicacion.mount("/static", StaticFiles(directory=DIRECTORIO_ESTATICO), name="static")
    aplicacion.include_router(router_panel)
    aplicacion.include_router(router_auth, prefix="/api")
    aplicacion.include_router(router_salud, prefix="/api")
    aplicacion.include_router(router_simulacion, prefix="/api")
    aplicacion.include_router(router_incidentes, prefix="/api")
    aplicacion.include_router(router_metricas, prefix="/api")
    aplicacion.include_router(router_baneos, prefix="/api")
    aplicacion.include_router(router_dispositivos, prefix="/api")
    aplicacion.include_router(router_eventos, prefix="/api")
    aplicacion.include_router(router_lista_blanca, prefix="/api")
    return aplicacion


def _sembrar_lista_blanca(motor: object, redes_config: tuple[str, ...]) -> None:
    """Pb-18: crea las entradas predeterminadas de la lista blanca si no existen.

    Se ejecuta al arrancar el servicio.  Las entradas predeterminadas se marcan
    con ``predeterminada=True`` para que la API no las elimine.
    """
    from sqlmodel import Session as _Session

    entradas_default = [
        (red, "Entrada predeterminada (configuración)") for red in redes_config
    ]
    with _Session(motor) as sesion:  # type: ignore[arg-type]
        for ip_o_red, descripcion in entradas_default:
            existe = sesion.exec(
                select(ListaBlanca).where(ListaBlanca.ip_o_red == ip_o_red)
            ).first()
            if existe is None:
                sesion.add(
                    ListaBlanca(
                        ip_o_red=ip_o_red,
                        descripcion=descripcion,
                        predeterminada=True,
                    )
                )
        sesion.commit()


def crear_generador_informes(configuracion: Ajustes) -> GeneradorInformes:
    if not configuracion.ollama_url:
        return GeneradorPlantilla()
    return GeneradorOllama(
        configuracion.ollama_url,
        configuracion.ollama_modelo,
        configuracion.timeout_ia_segundos,
    )


app = crear_aplicacion()
