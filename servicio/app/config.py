from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
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
    eve_json: Path = Path("/var/log/suricata/eve.json")
    fail2ban_binario: Path = Path("/usr/bin/fail2ban-client")
    fail2ban_jail: str = "defensa-web"
    jwt_secret: SecretStr | None = None
    token_minutos: int = Field(default=480, ge=5, le=1440)
    admin_usuario: str = "admin"
    admin_password: SecretStr | None = None
    modelo_clasificador: Path | None = None
    umbral_confianza: float = Field(default=0.6, ge=0, le=1)
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_modelo: str | None = None
    timeout_ia_segundos: float = Field(default=20, gt=0, le=120)
    fcm_credenciales: Path | None = None

    @field_validator("lista_blanca", mode="before")
    @classmethod
    def separar_lista_blanca(cls, valor: object) -> object:
        if isinstance(valor, str):
            return tuple(parte.strip() for parte in valor.split(",") if parte.strip())
        return valor

    @field_validator(
        "jwt_secret",
        "admin_password",
        "modelo_clasificador",
        "ollama_modelo",
        "fcm_credenciales",
        mode="before",
    )
    @classmethod
    def vacio_como_nulo(cls, valor: object) -> object:
        return None if valor == "" else valor

    @model_validator(mode="after")
    def validar_produccion(self) -> "Ajustes":
        if self.modo == "real":
            if self.jwt_secret is None or not self.jwt_secret.get_secret_value():
                raise ValueError("DEFENSA_JWT_SECRET es obligatorio en modo real")
            if self.admin_password is None or not self.admin_password.get_secret_value():
                raise ValueError("DEFENSA_ADMIN_PASSWORD es obligatorio en modo real")
        return self


@lru_cache
def obtener_ajustes() -> Ajustes:
    return Ajustes()
