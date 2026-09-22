from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.dominio.modelos import Auditoria, ListaBlanca
from app.main import _sembrar_lista_blanca


def _cabeceras(cliente: TestClient) -> dict[str, str]:
    respuesta = cliente.post(
        "/api/auth/login",
        json={"usuario": "admin", "contrasena": "contrasena-de-pruebas"},
    )
    assert respuesta.status_code == 200
    return {"Authorization": f"Bearer {respuesta.json()['access_token']}"}


def test_lista_blanca_exige_autenticacion_y_marca_predeterminadas(cliente: TestClient) -> None:
    assert cliente.get("/api/lista-blanca").status_code == 401
    entradas = cliente.get("/api/lista-blanca", headers=_cabeceras(cliente))

    assert entradas.status_code == 200
    assert {item["ip_o_red"] for item in entradas.json()} == {"127.0.0.0/8", "::1/128"}
    assert all(item["predeterminada"] for item in entradas.json())


def test_alta_validacion_baja_y_auditoria(cliente: TestClient) -> None:
    cabeceras = _cabeceras(cliente)
    invalida = cliente.post("/api/lista-blanca", json={"ip_o_red": "no-es-ip"}, headers=cabeceras)
    assert invalida.status_code == 422

    alta = cliente.post(
        "/api/lista-blanca",
        json={"ip_o_red": "10.10.10.4/24", "descripcion": "Red de prueba"},
        headers=cabeceras,
    )
    assert alta.status_code == 201
    assert alta.json()["ip_o_red"] == "10.10.10.0/24"
    assert alta.json()["predeterminada"] is False
    assert (
        cliente.post(
            "/api/lista-blanca", json={"ip_o_red": "10.10.10.0/24"}, headers=cabeceras
        ).status_code
        == 409
    )

    predeterminadas = cliente.get("/api/lista-blanca", headers=cabeceras).json()
    protegida = next(item for item in predeterminadas if item["predeterminada"])
    assert (
        cliente.delete(f"/api/lista-blanca/{protegida['id']}", headers=cabeceras).status_code == 403
    )
    assert (
        cliente.delete(f"/api/lista-blanca/{alta.json()['id']}", headers=cabeceras).status_code
        == 200
    )
    with Session(cliente.app.state.motor) as sesion:
        auditorias = list(sesion.exec(select(Auditoria)).all())
        entradas = list(sesion.exec(select(ListaBlanca)).all())

    assert [(item.actor, item.accion, item.ip_afectada) for item in auditorias] == [
        ("admin", "lista_blanca_alta", "10.10.10.0/24"),
        ("admin", "lista_blanca_baja", "10.10.10.0/24"),
    ]
    assert all(item.fecha_utc <= datetime.now(UTC).replace(tzinfo=None) for item in auditorias)
    assert {item.ip_o_red for item in entradas} == {"127.0.0.0/8", "::1/128"}


def test_sembrar_marca_entrada_existente_como_predeterminada(cliente: TestClient) -> None:
    motor = cliente.app.state.motor
    with Session(motor) as sesion:
        entrada = sesion.exec(
            select(ListaBlanca).where(ListaBlanca.ip_o_red == "127.0.0.0/8")
        ).one()
        entrada.predeterminada = False
        sesion.add(entrada)
        sesion.commit()

    _sembrar_lista_blanca(motor, ("127.0.0.0/8", "::1/128"))

    with Session(motor) as sesion:
        entrada = sesion.exec(
            select(ListaBlanca).where(ListaBlanca.ip_o_red == "127.0.0.0/8")
        ).one()
        assert entrada.predeterminada is True


def test_red_dinamica_evitar_baneo_y_baja_reactiva_politica(cliente: TestClient) -> None:
    cabeceras = _cabeceras(cliente)
    alta = cliente.post("/api/lista-blanca", json={"ip_o_red": "192.0.2.60"}, headers=cabeceras)
    assert alta.status_code == 201
    entrada = {
        "fecha_utc": datetime.now(UTC).isoformat(),
        "ip_origen": "192.0.2.60",
        "sid": 1000001,
        "firma": "SQLi de prueba",
        "categoria": "sqli",
        "severidad_firma": 1,
    }
    respuestas = [
        cliente.post("/api/simulacion/eventos", json=entrada, headers=cabeceras) for _ in range(5)
    ]
    assert all(respuesta.status_code == 201 for respuesta in respuestas)
    assert all(respuesta.json()["baneo_id"] is None for respuesta in respuestas)

    baja = cliente.delete(f"/api/lista-blanca/{alta.json()['id']}", headers=cabeceras)
    assert baja.status_code == 200
    despues = cliente.post("/api/simulacion/eventos", json=entrada, headers=cabeceras)
    assert despues.status_code == 201
    assert despues.json()["baneo_id"] is not None
