import asyncio
from datetime import UTC, datetime

from fastapi.testclient import TestClient


def evento(ip: str = "192.0.2.10") -> dict[str, object]:
    return {
        "fecha_utc": datetime.now(UTC).isoformat(),
        "ip_origen": ip,
        "sid": 1000001,
        "firma": "SQLi de prueba",
        "categoria": "sqli",
        "severidad_firma": 1,
        "metodo": "GET",
        "url": "/buscar?q=' OR 1=1--",
    }


def test_salud_informa_modo_simulado(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "estado": "operativo",
        "modo": "simulado",
        "entorno": "pruebas",
    }


def test_cinco_eventos_crean_un_incidente_y_un_baneo(cliente: TestClient) -> None:
    respuestas = [cliente.post("/api/simulacion/eventos", json=evento()) for _ in range(5)]
    sexto = cliente.post("/api/simulacion/eventos", json=evento())

    assert all(respuesta.status_code == 201 for respuesta in respuestas)
    incidentes = {respuesta.json()["incidente_id"] for respuesta in respuestas}
    assert len(incidentes) == 1
    assert respuestas[-1].json()["baneo_id"] is not None
    assert sexto.status_code == 201
    assert sexto.json()["baneo_id"] is None
    bloqueos = asyncio.run(cliente.app.state.actuador.bloqueos())
    assert list(bloqueos) == ["192.0.2.10"]


def test_lista_blanca_nunca_se_banea(cliente: TestClient) -> None:
    respuestas = [
        cliente.post("/api/simulacion/eventos", json=evento("127.0.0.1")) for _ in range(5)
    ]

    assert all(respuesta.status_code == 201 for respuesta in respuestas)
    assert all(respuesta.json()["baneo_id"] is None for respuesta in respuestas)
    assert asyncio.run(cliente.app.state.actuador.bloqueos()) == {}


def test_ip_invalida_se_rechaza_sin_accion_externa(cliente: TestClient) -> None:
    respuesta = cliente.post("/api/simulacion/eventos", json=evento("no-es-ip"))

    assert respuesta.status_code == 422
    assert asyncio.run(cliente.app.state.actuador.bloqueos()) == {}
