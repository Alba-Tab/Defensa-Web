import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Protocol

from app.dominio.esquemas import EventoEntrada


@dataclass(frozen=True)
class Clasificacion:
    tipo: str
    confianza: float
    severidad: int | None


class Clasificador(Protocol):
    async def clasificar(self, evento: EventoEntrada) -> Clasificacion: ...


class ClasificadorNulo:
    async def clasificar(self, evento: EventoEntrada) -> Clasificacion:
        del evento
        return Clasificacion(tipo="indeterminado", confianza=0.0, severidad=None)


class ClasificadorJoblib:
    _severidades: ClassVar[dict[str, int]] = {
        "sqli": 3,
        "xss": 3,
        "traversal": 3,
        "escaneo": 2,
        "sondeo_archivos": 2,
        "fuerza_bruta": 2,
        "benigno": 1,
    }

    def __init__(self, ruta_modelo: Path, umbral: float) -> None:
        import joblib  # type: ignore[import-untyped]

        self._modelo = joblib.load(ruta_modelo)
        self._umbral = umbral

    @staticmethod
    def _texto(evento: EventoEntrada) -> str:
        return " ".join(
            parte
            for parte in (
                evento.metodo,
                evento.uri_decodificada or evento.url,
                evento.parametros,
                evento.cuerpo_fragmento,
                evento.user_agent,
                evento.categoria,
            )
            if parte
        )

    def _clasificar_sincrono(self, evento: EventoEntrada) -> Clasificacion:
        probabilidades = self._modelo.predict_proba([self._texto(evento)])[0]
        indice = int(probabilidades.argmax())
        confianza = float(probabilidades[indice])
        tipo = str(self._modelo.classes_[indice])
        if confianza < self._umbral:
            return Clasificacion("indeterminado", confianza, None)
        return Clasificacion(tipo, confianza, self._severidades.get(tipo))

    async def clasificar(self, evento: EventoEntrada) -> Clasificacion:
        return await asyncio.to_thread(self._clasificar_sincrono, evento)
