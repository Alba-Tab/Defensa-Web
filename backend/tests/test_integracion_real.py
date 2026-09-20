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
            "signature_id": 1000001,
            "signature": "SQLi de prueba",
            "category": "Web Application Attack",
            "severity": 1,
        },
        "http": {"http_method": "GET", "url": "/buscar?q=1"},
    }
    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(alerta) + "\n")
        archivo.flush()

    evento = await asyncio.wait_for(siguiente, timeout=1)

    assert evento.ip_origen == "192.0.2.80"
    assert evento.sid == 1000001
    assert evento.url == "/buscar?q=1"


def test_mapeo_owasp_para_ataques_del_mvp() -> None:
    assert categoria_owasp("sqli", "") == "A05:2025 - Injection"
    assert categoria_owasp("fuerza_bruta", "") == "A07:2025 - Authentication Failures"
