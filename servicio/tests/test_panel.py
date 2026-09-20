from pathlib import Path

from fastapi.testclient import TestClient

from app.web import DIRECTORIO_PLANTILLAS


def test_panel_carga_el_esqueleto_y_dependencias_locales(cliente: TestClient) -> None:
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert "data-panel-esqueleto" in respuesta.text
    for recurso in (
        "/static/vendor/htmx.min.js",
        "/static/vendor/alpine.min.js",
        "/static/vendor/chart.umd.js",
        "/static/css/panel.css",
        "/static/js/panel.js",
    ):
        assert recurso in respuesta.text
        assert cliente.get(recurso).status_code == 200


def test_plantillas_no_referencian_recursos_remotos() -> None:
    contenido = "\n".join(
        archivo.read_text(encoding="utf-8")
        for archivo in Path(DIRECTORIO_PLANTILLAS).glob("*.html")
    )

    assert "https://" not in contenido
    assert "http://" not in contenido
    assert "//cdn." not in contenido
