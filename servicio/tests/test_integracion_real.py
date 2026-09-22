import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.componentes.actuador import DryRunActuator
from app.componentes.clasificador import Clasificacion, ClasificadorNulo
from app.componentes.correlador import Correlador
from app.componentes.fuente_eventos import EveSource
from app.componentes.politicas import MotorPoliticas
from app.dominio.modelos import Baneo, Evento, Incidente
from app.integracion import categoria_owasp
from app.servicios import ProcesadorEventos


@pytest.mark.asyncio
async def test_eve_source_convierte_una_alerta_nueva(tmp_path: Path) -> None:
    ruta = tmp_path / "eve.json"
    ruta.write_text("", encoding="utf-8")
    fuente = EveSource(ruta, intervalo_segundos=0.01)
    siguiente = asyncio.create_task(anext(fuente.eventos()))
    await asyncio.sleep(0.02)
    alerta = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "alert",
        "src_ip": "192.0.2.80",
        "alert": {
            "action": "blocked",
            "signature_id": 1000001,
            "signature": "SQLi de prueba",
            "category": "Web Application Attack",
            "severity": 1,
        },
        "http": {
            "http_method": "GET",
            "url": "/buscar?q=1%27+OR+1%3D1--",
            "http_user_agent": "sqlmap/1.8",
        },
    }
    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(alerta) + "\n")
        archivo.flush()

    evento = await asyncio.wait_for(siguiente, timeout=1)

    assert evento.ip_origen == "192.0.2.80"
    assert evento.sid == 1000001
    assert evento.firma == "SQLi de prueba"
    assert evento.categoria == "Web Application Attack"
    assert evento.severidad_firma == 1
    assert evento.accion == "descarte"
    assert evento.metodo == "GET"
    assert evento.url == "/buscar?q=1%27+OR+1%3D1--"
    assert evento.uri_decodificada == "/buscar"
    assert evento.parametros == "q=1' OR 1=1--"
    assert evento.user_agent == "sqlmap/1.8"
    assert evento.fecha_utc.utcoffset() == timedelta(0)


@pytest.mark.asyncio
async def test_eve_source_no_pierde_eventos_al_rotar(tmp_path: Path) -> None:
    ruta = tmp_path / "eve.json"
    rotado = tmp_path / "eve.json.1"
    ruta.write_text("", encoding="utf-8")
    fuente = EveSource(ruta, intervalo_segundos=0.01)
    iterador = fuente.eventos()
    primero_pendiente = asyncio.create_task(anext(iterador))
    await asyncio.sleep(0.02)

    def alerta(sid: int) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event_type": "alert",
                "src_ip": "192.0.2.80",
                "alert": {
                    "signature_id": sid,
                    "signature": "SQLi de prueba",
                    "category": "Web Application Attack",
                    "severity": 1,
                },
                "http": {"http_method": "GET", "url": f"/buscar?q={sid}"},
            }
        )

    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(alerta(1000001) + "\n")
        archivo.flush()
    primero = await asyncio.wait_for(primero_pendiente, timeout=1)

    ruta.rename(rotado)
    ruta.write_text(alerta(1000002) + "\n", encoding="utf-8")
    segundo = await asyncio.wait_for(anext(iterador), timeout=1)
    await iterador.aclose()

    assert primero.sid == 1000001
    assert segundo.sid == 1000002


def test_eve_source_ignora_trafico_sin_alerta() -> None:
    linea_http_legitima = json.dumps(
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": "http",
            "src_ip": "192.0.2.81",
            "http": {"http_method": "GET", "url": "/buscar?q=teclado"},
        }
    )

    assert EveSource._convertir(linea_http_legitima) is None


@pytest.mark.parametrize(
    ("sid", "categoria"),
    [(1000002, "sondeo_archivos"), (1000003, "sondeo_archivos"), (1000004, "escaneo")],
)
def test_firmas_locales_tienen_categoria_de_hu(sid: int, categoria: str) -> None:
    linea = json.dumps(
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": "alert",
            "src_ip": "192.0.2.80",
            "alert": {
                "signature_id": sid,
                "signature": "Firma local de prueba",
                "category": "Web Application Attack",
                "severity": 2,
            },
            "http": {"http_method": "GET", "url": "/.env"},
        }
    )

    evento = EveSource._convertir(linea)

    assert evento is not None
    assert evento.categoria == categoria


@pytest.mark.asyncio
async def test_cien_alertas_de_escaneo_crean_un_incidente_y_un_baneo() -> None:
    motor = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(motor)
    procesador = ProcesadorEventos(
        Correlador(300),
        MotorPoliticas(
            DryRunActuator(),
            umbral_eventos=5,
            ventana_segundos=60,
            duracion_segundos=600,
            lista_blanca=("127.0.0.0/8",),
        ),
        ClasificadorNulo(),
    )
    resultados = []
    with Session(motor) as sesion:
        for indice in range(120):
            linea = json.dumps(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "event_type": "alert",
                    "src_ip": "192.0.2.55",
                    "alert": {
                        "signature_id": 1000004,
                        "signature": "DEFENSA escaneo web detectado (Nikto/ffuf)",
                        "category": "Web Application Attack",
                        "severity": 2,
                    },
                    "http": {
                        "http_method": "GET",
                        "url": f"/ruta-{indice}",
                        "http_user_agent": "Fuzz Faster U Fool v2.1.0",
                    },
                }
            )
            entrada = EveSource._convertir(linea)
            assert entrada is not None
            resultados.append(await procesador.procesar(entrada, sesion))

        incidentes = list(sesion.exec(select(Incidente)).all())
        eventos = list(sesion.exec(select(Evento)).all())
        baneos = list(sesion.exec(select(Baneo)).all())

    assert len(incidentes) == 1
    assert incidentes[0].tipo_ataque == "escaneo"
    assert len(eventos) == 120
    assert len(baneos) == 1
    assert resultados[4].baneo_id == baneos[0].id
    assert all(resultado.incidente_id == incidentes[0].id for resultado in resultados)


@pytest.mark.asyncio
async def test_firma_de_sondeo_prevalece_sobre_prediccion_ia_de_escaneo() -> None:
    class ClasificadorEquivocado:
        async def clasificar(self, evento: object) -> Clasificacion:
            del evento
            return Clasificacion(tipo="escaneo", confianza=0.99, severidad=2)

    motor = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(motor)
    procesador = ProcesadorEventos(
        Correlador(300),
        MotorPoliticas(
            DryRunActuator(),
            umbral_eventos=5,
            ventana_segundos=60,
            duracion_segundos=600,
            lista_blanca=(),
        ),
        ClasificadorEquivocado(),
    )
    entrada = EveSource._convertir(
        json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event_type": "alert",
                "src_ip": "192.0.2.56",
                "alert": {
                    "signature_id": 1000002,
                    "signature": "DEFENSA sondeo de archivo sensible",
                    "category": "Web Application Attack",
                    "severity": 2,
                },
                "http": {"http_method": "GET", "url": "/.env"},
            }
        )
    )
    assert entrada is not None
    with Session(motor) as sesion:
        resultado = await procesador.procesar(entrada, sesion)
        evento = sesion.exec(select(Evento)).one()

    assert resultado.tipo_ataque == "sondeo_archivos"
    assert evento.clase_ia == "escaneo"


def test_mapeo_owasp_para_ataques_del_mvp() -> None:
    assert categoria_owasp("sqli", "") == "A05:2025 - Injection"
    assert categoria_owasp("fuerza_bruta", "") == "A07:2025 - Authentication Failures"
