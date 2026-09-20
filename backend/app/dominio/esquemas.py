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
    incidente_nuevo: bool


class CredencialesEntrada(BaseModel):
    usuario: str = Field(min_length=1, max_length=100)
    contrasena: str = Field(min_length=1, max_length=256)


class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class DispositivoEntrada(BaseModel):
    token_fcm: str = Field(min_length=16, max_length=4096)
    plataforma: str = Field(pattern="^(android|ios)$")


class IncidenteSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ip_origen: str
    categoria: str
    tipo_ataque: str
    severidad: int
    estado: str
    inicio: datetime
    ultima_actividad: datetime
    confianza_clasificador: float | None
    categoria_owasp: str | None
    informe: str | None
    origen_informe: str | None


class BaneoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ip: str
    inicio: datetime
    expira: datetime
    estado: str
    nivel_reincidencia: int
    incidente_id: int
