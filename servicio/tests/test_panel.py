from pathlib import Path

from fastapi.testclient import TestClient

from app.web import DIRECTORIO_PLANTILLAS


def test_panel_exige_sesion_y_carga_las_historias_web(cliente: TestClient) -> None:
    sin_sesion = cliente.get("/", follow_redirects=False)
    assert sin_sesion.status_code == 303
    assert sin_sesion.headers["location"] == "/login"

    sesion = cliente.post(
        "/api/auth/sesion",
        json={"usuario": "admin", "contrasena": "contrasena-de-pruebas"},
    )
    assert sesion.status_code == 200
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert 'hx-post="/api/auth/logout"' in respuesta.text
    for elemento in (
        "filtros-incidentes",
        "lista-incidentes",
        "lista-componentes",
        "grafico-incidentes",
        "grafico-tipos",
        "lista-bloqueos",
        "detalle-incidente",
    ):
        assert f'id="{elemento}"' in respuesta.text
    for recurso in (
        "/static/vendor/htmx.min.js",
        "/static/vendor/alpine.min.js",
        "/static/vendor/chart.umd.js",
        "/static/css/panel.css",
        "/static/js/panel.js",
    ):
        assert recurso in respuesta.text
        assert cliente.get(recurso).status_code == 200
    assert cliente.get("/static/js/login.js").status_code == 200


def test_plantillas_no_referencian_recursos_remotos() -> None:
    contenido = "\n".join(
        archivo.read_text(encoding="utf-8")
        for archivo in Path(DIRECTORIO_PLANTILLAS).glob("*.html")
    )

    assert "https://" not in contenido
    assert "http://" not in contenido
    assert "//cdn." not in contenido
