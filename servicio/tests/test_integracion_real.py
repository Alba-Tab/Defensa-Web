import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.componentes.fuente_eventos import EveSource
from app.integracion import categoria_owasp


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
    assert evento.fecha_utc.tzinfo is None


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


def test_mapeo_owasp_para_ataques_del_mvp() -> None:
    assert categoria_owasp("sqli", "") == "A05:2025 - Injection"
    assert categoria_owasp("fuerza_bruta", "") == "A07:2025 - Authentication Failures"
