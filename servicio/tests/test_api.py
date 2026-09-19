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
        "fuente_eventos": "FakeSource",
        "actuador": "DryRunActuator",
        "clasificador": "ClasificadorNulo",
        "notificador": "NotificadorNulo",
    }


def iniciar_sesion(cliente: TestClient) -> str:
    respuesta = cliente.post(
        "/api/auth/login",
        json={"usuario": "admin", "contrasena": "contrasena-de-pruebas"},
    )
    assert respuesta.status_code == 200
    return str(respuesta.json()["access_token"])


def test_api_operativa_exige_token(cliente: TestClient) -> None:
    sin_token = cliente.get("/api/incidentes")
    token = iniciar_sesion(cliente)
    con_token = cliente.get("/api/incidentes", headers={"Authorization": f"Bearer {token}"})

    assert sin_token.status_code == 401
    assert con_token.status_code == 200


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


def test_circuito_movil_lista_y_libera_baneo(cliente: TestClient) -> None:
    for _ in range(5):
        assert cliente.post("/api/simulacion/eventos", json=evento("192.0.2.44")).status_code == 201
    token = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token}"}

    incidentes = cliente.get("/api/incidentes", headers=cabeceras)
    baneos = cliente.get("/api/baneos", headers=cabeceras)
    liberacion = cliente.post("/api/baneos/192.0.2.44/liberar", headers=cabeceras)
    baneos_actualizados = cliente.get("/api/baneos", headers=cabeceras)

    assert incidentes.status_code == 200
    assert incidentes.json()[0]["ip_origen"] == "192.0.2.44"
    assert baneos.json()[0]["estado"] == "vigente"
    assert liberacion.json() == {"estado": "liberado", "ip": "192.0.2.44"}
    assert baneos_actualizados.json()[0]["estado"] == "liberado"
