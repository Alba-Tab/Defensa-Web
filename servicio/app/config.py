import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


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
    intervalo_mantenimiento_segundos: float = Field(default=5, gt=0, le=300)
    lista_blanca: Annotated[tuple[str, ...], NoDecode] = ("127.0.0.0/8", "::1/128")
    eve_json: Path = Path("/var/log/suricata/eve.json")
    nginx_access_log: Path = Path("/var/log/nginx/access.log")
    brute_force_umbral: int = Field(default=5, ge=1, le=100)
    brute_force_ventana_segundos: int = Field(default=600, ge=1)
    systemctl_binario: Path = Path("/usr/bin/systemctl")
    suricata_servicio: str = "suricata"
    salud_timeout_segundos: float = Field(default=2, gt=0, le=10)
    fail2ban_binario: Path = Path("/usr/bin/fail2ban-client")
    fail2ban_jail: str = "defensa-web"
    nginx_servicio: str = "nginx"
    fail2ban_servicio: str = "fail2ban"
    ollama_url: str | None = None
    ollama_modelo: str = Field(default="llama3.2:1b", min_length=1)
    jwt_secret: SecretStr | None = None
    token_minutos: int = Field(default=480, ge=5, le=1440)
    login_max_intentos: int = Field(default=5, ge=1, le=100)
    login_ventana_segundos: int = Field(default=60, ge=1)
    login_bloqueo_segundos: int = Field(default=300, ge=1)
    admin_usuario: str = "admin"
    admin_password: SecretStr | None = None
    modelo_clasificador: Path | None = None
    umbral_confianza: float = Field(default=0.6, ge=0, le=1)
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_api_key: SecretStr | None = None
    openrouter_modelo: str | None = None
    openrouter_referer: str | None = None
    timeout_ia_segundos: float = Field(default=20, gt=0, le=120)
    fcm_credenciales: Path | None = None

    @field_validator("lista_blanca", mode="before")
    @classmethod
    def separar_lista_blanca(cls, valor: object) -> object:
        if isinstance(valor, str):
            texto = valor.strip()
            if texto.startswith("["):
                return tuple(json.loads(texto))
            return tuple(parte.strip() for parte in texto.split(",") if parte.strip())
        return valor

    @field_validator(
        "jwt_secret",
        "admin_password",
        "modelo_clasificador",
        "openrouter_api_key",
        "openrouter_modelo",
        "openrouter_referer",
        "ollama_url",
        "fcm_credenciales",
        mode="before",
    )
    @classmethod
    def vacio_como_nulo(cls, valor: object) -> object:
        return None if valor == "" else valor

    @model_validator(mode="after")
    def validar_produccion(self) -> "Ajustes":
        ia_configurada = self.openrouter_api_key is not None
        modelo_configurado = self.openrouter_modelo is not None
        if ia_configurada != modelo_configurado:
            raise ValueError(
                "DEFENSA_OPENROUTER_API_KEY y DEFENSA_OPENROUTER_MODELO deben configurarse juntos"
            )
        if self.modo == "real":
            if self.jwt_secret is None or not self.jwt_secret.get_secret_value():
                raise ValueError("DEFENSA_JWT_SECRET es obligatorio en modo real")
            if self.admin_password is None or not self.admin_password.get_secret_value():
                raise ValueError("DEFENSA_ADMIN_PASSWORD es obligatorio en modo real")
        return self


@lru_cache
def obtener_ajustes() -> Ajustes:
    return Ajustes()
