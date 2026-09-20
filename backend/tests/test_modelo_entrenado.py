import asyncio
from datetime import datetime
from pathlib import Path

from app.componentes.clasificador import ClasificadorJoblib
from app.dominio.esquemas import EventoEntrada


def test_artefacto_demo_es_compatible_con_el_backend() -> None:
    ruta = Path(__file__).parents[2] / "backend" / "modelos" / "clasificador.joblib"
    clasificador = ClasificadorJoblib(ruta, umbral=0.0)
    evento = EventoEntrada(
        fecha_utc=datetime(2026, 9, 19, 12, 0, 0),
        ip_origen="192.0.2.20",
        sid=1000001,
        firma="SQLi de prueba",
        categoria="web-application-attack",
        severidad_firma=1,
        metodo="GET",
        url="/buscar?q=' OR 1=1--",
    )

    resultado = asyncio.run(clasificador.clasificar(evento))

    assert resultado.tipo in {
        "benigno",
        "escaneo",
        "fuerza_bruta",
        "sqli",
        "traversal",
        "xss",
    }
    assert 0 <= resultado.confianza <= 1
