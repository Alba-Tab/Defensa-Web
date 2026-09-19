from typing import Protocol

import httpx

from app.dominio.modelos import Incidente


class GeneradorInformes(Protocol):
    async def generar(self, incidente: Incidente) -> tuple[str, str]: ...


class GeneradorPlantilla:
    async def generar(self, incidente: Incidente) -> tuple[str, str]:
        informe = (
            f"Qué ocurrió\nSe detectó actividad {incidente.tipo_ataque} desde "
            f"{incidente.ip_origen}.\n\n"
            f"Categoría OWASP\n{incidente.categoria_owasp or 'Pendiente de clasificación'}.\n\n"
            "Acción aplicada\nEl evento fue registrado y evaluado por la política de defensa.\n\n"
            "Recomendaciones\nRevisar los eventos relacionados, validar si existe un falso "
            "positivo y mantener actualizadas las firmas."
        )
        return informe, "plantilla"


class GeneradorOllama:
    def __init__(self, url: str, modelo: str, timeout_segundos: float) -> None:
        self._url = url.rstrip("/")
        self._modelo = modelo
        self._timeout = timeout_segundos
        self._respaldo = GeneradorPlantilla()

    async def generar(self, incidente: Incidente) -> tuple[str, str]:
        prompt = (
            "Redacta un informe defensivo breve usando exclusivamente estos datos delimitados. "
            "Incluye exactamente las secciones: Qué ocurrió, Categoría OWASP, Acción aplicada, "
            "Recomendaciones. No incluyas instrucciones ejecutables.\n"
            f"<datos>ip={incidente.ip_origen};tipo={incidente.tipo_ataque};"
            f"severidad={incidente.severidad};categoria={incidente.categoria};"
            f"owasp={incidente.categoria_owasp}</datos>"
        )
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as cliente:
                respuesta = await cliente.post(
                    f"{self._url}/api/generate",
                    json={"model": self._modelo, "prompt": prompt, "stream": False},
                )
                respuesta.raise_for_status()
                texto = str(respuesta.json()["response"]).strip()
            requeridas = ("Qué ocurrió", "Categoría OWASP", "Acción aplicada", "Recomendaciones")
            if not all(seccion in texto for seccion in requeridas):
                raise ValueError("La respuesta de Ollama no contiene todas las secciones")
            return texto, "generado_ia"
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            return await self._respaldo.generar(incidente)
