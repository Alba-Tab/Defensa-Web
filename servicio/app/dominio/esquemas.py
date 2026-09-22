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
    accion: str = Field(default="alerta", pattern="^(alerta|descarte)$")
    metodo: str | None = Field(default=None, max_length=16)
    url: str | None = Field(default=None, max_length=2048)
    uri_decodificada: str | None = Field(default=None, max_length=2048)
    parametros: str | None = Field(default=None, max_length=4096)
    cuerpo_fragmento: str | None = Field(default=None, max_length=2048)
    user_agent: str | None = Field(default=None, max_length=1024)

    @field_validator("ip_origen")
    @classmethod
    def validar_ip(cls, valor: str) -> str:
        return str(ip_address(valor))

    @field_validator("fecha_utc")
    @classmethod
    def normalizar_fecha_utc(cls, valor: datetime) -> datetime:
        if valor.tzinfo is None:
            return valor.replace(tzinfo=UTC)
        return valor.astimezone(UTC)


class ResultadoProcesamiento(BaseModel):
    incidente_id: int
    evento_id: int
    baneo_id: int | None = None
    incidente_nuevo: bool
    tipo_ataque: str
    severidad: int
    ip_origen: str


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


class EventoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_utc: datetime
    ip_origen: str
    sid: int
    firma: str
    categoria: str
    severidad_firma: int
    accion: str
    metodo: str | None
    url: str | None
    uri_decodificada: str | None
    parametros: str | None
    cuerpo_fragmento: str | None
    user_agent: str | None
    clase_ia: str | None
    confianza_ia: float | None
    incidente_id: int


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
    severidad_notificada: int | None
    categoria_owasp: str | None
    informe: str | None
    origen_informe: str | None
    modelo_informe: str | None
    eventos: list[EventoSalida] = Field(default_factory=list)


class BaneoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ip: str
    inicio: datetime
    expira: datetime
    estado: str
    nivel_reincidencia: int
    incidente_id: int


class ListaBlancaEntrada(BaseModel):
    """Datos necesarios para agregar una entrada a la lista blanca (Pb-18)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ip_o_red: str = Field(min_length=1, max_length=50)
    descripcion: str | None = Field(default=None, max_length=300)

    @field_validator("ip_o_red")
    @classmethod
    def validar_cidr(cls, valor: str) -> str:
        from ipaddress import ip_network

        try:
            red = ip_network(valor, strict=False)
        except ValueError as error:
            raise ValueError(
                f"'{valor}' no es una dirección IP ni una red CIDR válida"
            ) from error
        return str(red)


class ListaBlancaSalida(BaseModel):
    """Representación de una entrada de la lista blanca en la respuesta (Pb-18)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ip_o_red: str
    descripcion: str | None
    predeterminada: bool

