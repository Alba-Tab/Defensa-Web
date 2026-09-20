import asyncio
from datetime import datetime
from pathlib import Path

from app.componentes.clasificador import ClasificadorJoblib
from app.dominio.esquemas import EventoEntrada


def test_artefacto_demo_es_compatible_con_el_backend() -> None:
    ruta = Path(__file__).parents[2] / "backend" / "modelos" / "clasificador.joblib"
    clasificador = ClasificadorJoblib(ruta, umbral=0.6)
    evento = EventoEntrada(
        fecha_utc=datetime(2026, 9, 19, 12, 0, 0),
        ip_origen="192.0.2.20",
        sid=1000001,
        firma="SQLi de prueba",
        categoria="web-application-attack",
        severidad_firma=1,
        metodo="GET",
        url="/buscar?q=' OR 1=1--",
        uri_decodificada="/buscar",
        parametros="q=' OR 1=1--",
        cuerpo_fragmento="",
        user_agent="sqlmap/1.8",
    )

    resultado = asyncio.run(clasificador.clasificar(evento))

    assert resultado.tipo == "sqli"
    assert resultado.confianza >= 0.6
    assert resultado.severidad == 3


def test_confianza_baja_devuelve_indeterminado_sin_severidad() -> None:
    ruta = Path(__file__).parents[2] / "backend" / "modelos" / "clasificador.joblib"
    clasificador = ClasificadorJoblib(ruta, umbral=0.99)
    evento = EventoEntrada(
        fecha_utc=datetime(2026, 9, 19, 12, 0, 0),
        ip_origen="192.0.2.20",
        sid=1000001,
        firma="SQLi",
        categoria="web-application-attack",
        severidad_firma=1,
        metodo="GET",
        uri_decodificada="/buscar",
        parametros="q=' OR 1=1--",
        user_agent="sqlmap/1.8",
    )

    resultado = asyncio.run(clasificador.clasificar(evento))

    assert resultado.tipo == "indeterminado"
    assert resultado.confianza < 0.99
    assert resultado.severidad is None


def test_texto_del_modelo_usa_todos_los_campos_requeridos() -> None:
    evento = EventoEntrada(
        fecha_utc=datetime(2026, 9, 19, 12, 0, 0),
        ip_origen="192.0.2.20",
        sid=1,
        firma="Prueba",
        categoria="categoria-firma",
        severidad_firma=2,
        metodo="POST",
        uri_decodificada="/ruta decodificada",
        parametros="a=1",
        cuerpo_fragmento="dato=cuerpo",
        user_agent="agente-prueba",
    )

    assert ClasificadorJoblib._texto(evento) == (
        "POST /ruta decodificada a=1 dato=cuerpo agente-prueba categoria-firma"
    )
