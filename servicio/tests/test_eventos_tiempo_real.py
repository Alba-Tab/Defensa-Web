import asyncio
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.eventos import _alertas_posteriores, _serializar_alerta
from app.componentes.eventos_tiempo_real import AlertaIncidente, BusEventos
from app.dominio.esquemas import ResultadoProcesamiento
from app.integracion import publicar_incidente_nuevo


def iniciar_sesion(cliente: TestClient) -> str:
    respuesta = cliente.post(
        "/api/auth/login",
        json={"usuario": "admin", "contrasena": "contrasena-de-pruebas"},
    )
    return str(respuesta.json()["access_token"])


def evento(ip: str) -> dict[str, object]:
    return {
        "fecha_utc": datetime.now(UTC).isoformat(),
        "ip_origen": ip,
        "sid": 1000001,
        "firma": "SQLi de prueba",
        "categoria": "sqli",
        "severidad_firma": 1,
        "metodo": "GET",
        "url": "/buscar?q=1",
    }


def test_sse_serializa_identificador_para_reconexion() -> None:
    salida = _serializar_alerta(
        AlertaIncidente(
            incidente_id=42,
            tipo_ataque="sqli",
            severidad=3,
            ip_origen="192.0.2.42",
        )
    )

    assert salida.startswith("id: 42\nevent: incidente\n")
    assert '"incidente_id": 42' in salida


@pytest.mark.asyncio
async def test_publica_solo_cuando_el_incidente_es_nuevo() -> None:
    bus = BusEventos()
    nuevo = ResultadoProcesamiento(
        incidente_id=42,
        evento_id=1,
        incidente_nuevo=True,
        tipo_ataque="sqli",
        severidad=3,
        ip_origen="192.0.2.42",
    )
    repetido = nuevo.model_copy(update={"evento_id": 2, "incidente_nuevo": False})

    async with bus.suscribir() as cola:
        publicar_incidente_nuevo(nuevo, bus)
        alerta = await asyncio.wait_for(cola.get(), timeout=1)
        cola.task_done()
        publicar_incidente_nuevo(repetido, bus)
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(cola.get(), timeout=0.02)

    assert alerta.incidente_id == 42


def test_reconexion_recupera_incidentes_posteriores_desde_sqlite(cliente: TestClient) -> None:
    token = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token}"}
    primero = cliente.post(
        "/api/simulacion/eventos", json=evento("192.0.2.101"), headers=cabeceras
    ).json()["incidente_id"]
    segundo = cliente.post(
        "/api/simulacion/eventos", json=evento("192.0.2.102"), headers=cabeceras
    ).json()["incidente_id"]

    alertas = _alertas_posteriores(cliente.app.state.motor, primero)

    assert [alerta.incidente_id for alerta in alertas] == [segundo]
    assert alertas[0].ip_origen == "192.0.2.102"
