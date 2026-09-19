from datetime import UTC, datetime
from ipaddress import ip_address

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventoEntrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    fecha_utc: datetime
    ip_origen: str
    sid: int
    firma: str = Field(min_length=1, max_length=500)
    categoria: str = Field(min_length=1, max_length=200)
    severidad_firma: int = Field(ge=1, le=3)
    metodo: str | None = Field(default=None, max_length=16)
    url: str | None = Field(default=None, max_length=2048)

    @field_validator("ip_origen")
    @classmethod
    def validar_ip(cls, valor: str) -> str:
        return str(ip_address(valor))

    @field_validator("fecha_utc")
    @classmethod
    def normalizar_fecha_utc(cls, valor: datetime) -> datetime:
        if valor.tzinfo is None:
            return valor
        return valor.astimezone(UTC).replace(tzinfo=None)


class ResultadoProcesamiento(BaseModel):
    incidente_id: int
    evento_id: int
    baneo_id: int | None = None
