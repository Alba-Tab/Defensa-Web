import httpx
import pytest

from app.componentes.informes import GeneradorOpenRouter
from app.dominio.modelos import Incidente


@pytest.mark.asyncio
async def test_openrouter_genera_informe_con_el_contrato_esperado() -> None:
    informe_esperado = (
        "Qué ocurrió\nActividad SQLi detectada.\n\n"
        "Categoría OWASP\nA05:2025 - Injection.\n\n"
        "Acción aplicada\nSe registró el incidente.\n\n"
        "Recomendaciones\nRevisar los eventos relacionados."
    )

    def responder(solicitud: httpx.Request) -> httpx.Response:
        assert solicitud.url == httpx.URL("https://openrouter.ai/api/v1/chat/completions")
        assert solicitud.headers["authorization"] == "Bearer clave-de-prueba"
        assert solicitud.headers["http-referer"] == "https://defensa.ejemplo"
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": informe_esperado}}]},
        )

    generador = GeneradorOpenRouter(
        "https://openrouter.ai/api/v1/chat/completions",
        "clave-de-prueba",
        "google/gemini-2.5-flash",
        1,
        "https://defensa.ejemplo",
        httpx.MockTransport(responder),
    )
    incidente = Incidente(
        ip_origen="192.0.2.20",
        categoria="sqli",
        tipo_ataque="sqli",
        severidad=1,
        categoria_owasp="A05:2025 - Injection",
    )

    informe, origen = await generador.generar(incidente)

    assert informe == informe_esperado
    assert origen == "openrouter"
