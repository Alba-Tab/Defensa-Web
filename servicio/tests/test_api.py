import asyncio
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.dominio.modelos import Auditoria, Dispositivo


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
    token = iniciar_sesion(cliente)
    respuesta = cliente.get("/api/salud", headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "estado": "operativo",
        "modo": "simulado",
        "entorno": "pruebas",
        "nginx": "no_aplica",
        "suricata": "no_aplica",
        "fail2ban": "no_aplica",
        "ollama": "no_configurado",
        "fuente_eventos": "FakeSource",
        "actuador": "DryRunActuator",
        "clasificador": "ClasificadorNulo",
        "notificador": "NotificadorNulo",
    }


def test_salud_informa_estado_degradado_si_suricata_esta_inactivo(
    cliente: TestClient,
) -> None:
    class MonitorInactivo:
        def estado(self) -> str:
            return "inactivo"

    cliente.app.state.monitor_suricata = MonitorInactivo()
    token = iniciar_sesion(cliente)

    respuesta = cliente.get("/api/salud", headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "degradado"
    assert respuesta.json()["suricata"] == "inactivo"


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


def test_historial_filtra_por_fecha_ip_y_severidad_y_valida_entrada(
    cliente: TestClient,
) -> None:
    token = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token}"}
    primero = evento("192.0.2.31")
    primero["fecha_utc"] = "2026-09-18T10:00:00Z"
    primero["severidad_firma"] = 1
    segundo = evento("192.0.2.32")
    segundo["fecha_utc"] = "2026-09-19T11:00:00Z"
    segundo["severidad_firma"] = 2
    cliente.post("/api/simulacion/eventos", json=primero, headers=cabeceras)
    cliente.post("/api/simulacion/eventos", json=segundo, headers=cabeceras)

    filtrados = cliente.get(
        "/api/incidentes",
        params={
            "desde": "2026-09-18T00:00:00Z",
            "hasta": "2026-09-18T23:59:59Z",
            "ip_origen": "192.0.2.31",
            "severidad": "3",
        },
        headers=cabeceras,
    )

    assert filtrados.status_code == 200
    assert [incidente["ip_origen"] for incidente in filtrados.json()] == ["192.0.2.31"]
    assert (
        cliente.get(
            "/api/incidentes", params={"ip_origen": "no-es-ip"}, headers=cabeceras
        ).status_code
        == 400
    )
    assert (
        cliente.get("/api/incidentes", params={"desde": "ayer"}, headers=cabeceras).status_code
        == 400
    )


def test_detalle_incidente_incluye_sus_eventos(cliente: TestClient) -> None:
    token = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token}"}
    creado = cliente.post("/api/simulacion/eventos", json=evento("192.0.2.30"), headers=cabeceras)

    respuesta = cliente.get(f"/api/incidentes/{creado.json()['incidente_id']}", headers=cabeceras)

    assert respuesta.status_code == 200
    assert len(respuesta.json()["eventos"]) == 1
    assert respuesta.json()["eventos"][0]["ip_origen"] == "192.0.2.30"
    assert respuesta.json()["eventos"][0]["accion"] == "alerta"
    assert respuesta.json()["eventos"][0]["clase_ia"] == "indeterminado"
    assert respuesta.json()["eventos"][0]["confianza_ia"] == 0


def test_registrar_dispositivo_es_idempotente_y_actualiza_fecha(cliente: TestClient) -> None:
    token_sesion = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token_sesion}"}
    token_fcm = "token-fcm-de-prueba-123456"

    primera = cliente.post(
        "/api/dispositivos",
        json={"token_fcm": token_fcm, "plataforma": "android"},
        headers=cabeceras,
    )
    with Session(cliente.app.state.motor) as sesion:
        antes = sesion.exec(select(Dispositivo).where(Dispositivo.token_fcm == token_fcm)).one()
        alta = antes.alta
        actualizado_antes = antes.actualizado_en
    segunda = cliente.post(
        "/api/dispositivos",
        json={"token_fcm": token_fcm, "plataforma": "ios"},
        headers=cabeceras,
    )

    with Session(cliente.app.state.motor) as sesion:
        dispositivos = list(sesion.exec(select(Dispositivo)).all())
    assert primera.status_code == 204
    assert segunda.status_code == 204
    assert len(dispositivos) == 1
    assert dispositivos[0].plataforma == "ios"
    assert dispositivos[0].alta == alta
    assert dispositivos[0].actualizado_en >= actualizado_antes


def test_cinco_eventos_crean_un_incidente_y_un_baneo(cliente: TestClient) -> None:
    token = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token}"}
    respuestas = [
        cliente.post("/api/simulacion/eventos", json=evento(), headers=cabeceras) for _ in range(5)
    ]
    sexto = cliente.post("/api/simulacion/eventos", json=evento(), headers=cabeceras)

    assert all(respuesta.status_code == 201 for respuesta in respuestas)
    incidentes = {respuesta.json()["incidente_id"] for respuesta in respuestas}
    assert len(incidentes) == 1
    assert respuestas[-1].json()["baneo_id"] is not None
    assert sexto.status_code == 201
    assert sexto.json()["baneo_id"] is None
    bloqueos = asyncio.run(cliente.app.state.actuador.bloqueos())
    assert list(bloqueos) == ["192.0.2.10"]


def test_lista_blanca_nunca_se_banea(cliente: TestClient) -> None:
    token = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token}"}
    respuestas = [
        cliente.post("/api/simulacion/eventos", json=evento("127.0.0.1"), headers=cabeceras)
        for _ in range(5)
    ]

    assert all(respuesta.status_code == 201 for respuesta in respuestas)
    assert all(respuesta.json()["baneo_id"] is None for respuesta in respuestas)
    assert asyncio.run(cliente.app.state.actuador.bloqueos()) == {}


def test_escaneo_se_correlaciona_y_banea_tras_el_umbral(cliente: TestClient) -> None:
    cabeceras = {"Authorization": f"Bearer {iniciar_sesion(cliente)}"}
    entrada = evento("192.0.2.51")
    entrada.update(
        sid=1000004,
        firma="DEFENSA escaneo web detectado (Nikto/ffuf)",
        categoria="escaneo",
        severidad_firma=2,
        url="/admin",
        user_agent="Nikto/2.5",
    )
    respuestas = [
        cliente.post("/api/simulacion/eventos", json=entrada, headers=cabeceras) for _ in range(5)
    ]

    assert all(respuesta.status_code == 201 for respuesta in respuestas)
    assert len({respuesta.json()["incidente_id"] for respuesta in respuestas}) == 1
    assert all(respuesta.json()["tipo_ataque"] == "escaneo" for respuesta in respuestas)
    assert respuestas[-1].json()["baneo_id"] is not None


def test_sondeo_archivos_conserva_tipo_aunque_ia_no_lo_reconozca(cliente: TestClient) -> None:
    cabeceras = {"Authorization": f"Bearer {iniciar_sesion(cliente)}"}
    respuestas = []
    for indice, ruta in enumerate(
        ("/.env", "/.git/config", "/config.php.bak", "/.env", "/.git/config")
    ):
        entrada = evento("192.0.2.52")
        entrada.update(
            sid=1000002 if indice != 2 else 1000003,
            firma="DEFENSA sondeo de archivo sensible",
            categoria="sondeo_archivos",
            severidad_firma=2,
            url=ruta,
        )
        respuestas.append(cliente.post("/api/simulacion/eventos", json=entrada, headers=cabeceras))

    assert all(respuesta.status_code == 201 for respuesta in respuestas)
    assert len({respuesta.json()["incidente_id"] for respuesta in respuestas}) == 1
    assert all(respuesta.json()["tipo_ataque"] == "sondeo_archivos" for respuesta in respuestas)
    assert respuestas[-1].json()["baneo_id"] is not None


def test_ip_invalida_se_rechaza_sin_accion_externa(cliente: TestClient) -> None:
    token = iniciar_sesion(cliente)
    respuesta = cliente.post(
        "/api/simulacion/eventos",
        json=evento("no-es-ip"),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert respuesta.status_code == 422
    assert asyncio.run(cliente.app.state.actuador.bloqueos()) == {}


def test_circuito_movil_lista_y_libera_baneo(cliente: TestClient) -> None:
    token = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token}"}
    for _ in range(5):
        assert (
            cliente.post(
                "/api/simulacion/eventos", json=evento("192.0.2.44"), headers=cabeceras
            ).status_code
            == 201
        )

    incidentes = cliente.get("/api/incidentes", headers=cabeceras)
    baneos = cliente.get("/api/baneos", headers=cabeceras)
    liberacion = cliente.post("/api/baneos/192.0.2.44/liberar", headers=cabeceras)
    baneos_actualizados = cliente.get("/api/baneos", headers=cabeceras)

    assert incidentes.status_code == 200
    assert incidentes.json()[0]["ip_origen"] == "192.0.2.44"
    assert baneos.json()[0]["estado"] == "vigente"
    assert liberacion.json() == {"estado": "liberado", "ip": "192.0.2.44"}
    assert baneos_actualizados.json()[0]["estado"] == "liberado"
    assert asyncio.run(cliente.app.state.actuador.bloqueos()) == {}
    segunda_liberacion = cliente.post("/api/baneos/192.0.2.44/liberar", headers=cabeceras)
    assert segunda_liberacion.status_code == 200
    with Session(cliente.app.state.motor) as sesion:
        auditorias = list(
            sesion.exec(
                select(Auditoria).where(
                    Auditoria.accion == "liberacion_manual",
                    Auditoria.ip_afectada == "192.0.2.44",
                )
            ).all()
        )
    assert auditorias
    assert all(auditoria.actor == "admin" for auditoria in auditorias)


def test_metricas_resumen_incidentes_bloqueos_tipos_y_top_ips(cliente: TestClient) -> None:
    token = iniciar_sesion(cliente)
    cabeceras = {"Authorization": f"Bearer {token}"}
    for _ in range(5):
        cliente.post("/api/simulacion/eventos", json=evento("192.0.2.90"), headers=cabeceras)

    respuesta = cliente.get("/api/metricas", headers=cabeceras)

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["resumen"]["incidentes_hoy"] >= 1
    assert datos["resumen"]["bloqueos_vigentes"] == 1
    assert len(datos["incidentes_por_hora"]) == 24
    assert datos["top_ips"][0] == {"ip": "192.0.2.90", "total": 1}
