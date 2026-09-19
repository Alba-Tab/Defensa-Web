from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Ajustes(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DEFENSA_",
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    entorno: Literal["desarrollo", "pruebas", "produccion"] = "desarrollo"
    modo: Literal["simulado", "real"] = "simulado"
    database_url: str = "sqlite:///./datos/defensa.db"
    umbral_eventos: int = Field(default=5, ge=1, le=1000)
    ventana_bloqueo_segundos: int = Field(default=60, ge=1)
    duracion_bloqueo_segundos: int = Field(default=600, ge=1)
    ventana_correlacion_segundos: int = Field(default=300, ge=1)
    lista_blanca: tuple[str, ...] = ("127.0.0.0/8", "::1/128")

    @field_validator("lista_blanca", mode="before")
    @classmethod
    def separar_lista_blanca(cls, valor: object) -> object:
        if isinstance(valor, str):
            return tuple(parte.strip() for parte in valor.split(",") if parte.strip())
        return valor


@lru_cache
def obtener_ajustes() -> Ajustes:
    return Ajustes()
