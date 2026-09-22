from datetime import UTC, datetime
from typing import ClassVar

from sqlalchemy import Index, text
from sqlmodel import Field, Relationship, SQLModel


def ahora_utc() -> datetime:
    return datetime.now(UTC)


def como_utc(fecha: datetime) -> datetime:
    """SQLite devuelve datetimes sin zona; los valores persistidos son UTC."""
    return fecha.replace(tzinfo=UTC) if fecha.tzinfo is None else fecha.astimezone(UTC)


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)
    hash_contrasena: str
    activo: bool = True
    creado_en: datetime = Field(default_factory=ahora_utc)


class Incidente(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ip_origen: str = Field(index=True)
    categoria: str
    tipo_ataque: str = "indeterminado"
    severidad: int = Field(ge=1, le=4)
    estado: str = "abierto"
    confianza_clasificador: float | None = None
    severidad_notificada: int | None = None
    categoria_owasp: str | None = None
    informe: str | None = None
    origen_informe: str | None = None
    modelo_informe: str | None = None
    inicio: datetime = Field(default_factory=ahora_utc)
    ultima_actividad: datetime = Field(default_factory=ahora_utc, index=True)
    eventos: list["Evento"] = Relationship(back_populates="incidente")
    baneos: list["Baneo"] = Relationship(back_populates="incidente")


class Evento(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fecha_utc: datetime = Field(default_factory=ahora_utc, index=True)
    ip_origen: str = Field(index=True)
    sid: int
    firma: str
    categoria: str
    severidad_firma: int = Field(ge=1, le=3)
    accion: str = "alerta"
    metodo: str | None = None
    url: str | None = None
    uri_decodificada: str | None = None
    parametros: str | None = None
    cuerpo_fragmento: str | None = None
    user_agent: str | None = None
    clase_ia: str | None = None
    confianza_ia: float | None = None
    incidente_id: int = Field(foreign_key="incidente.id")
    incidente: Incidente | None = Relationship(back_populates="eventos")


class Baneo(SQLModel, table=True):
    __table_args__ = (
        Index(
            "uq_baneo_ip_vigente",
            "ip",
            unique=True,
            sqlite_where=text("estado = 'vigente'"),
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    ip: str = Field(index=True)
    inicio: datetime = Field(default_factory=ahora_utc)
    expira: datetime
    estado: str = "vigente"
    nivel_reincidencia: int = 0
    incidente_id: int = Field(foreign_key="incidente.id")
    incidente: Incidente | None = Relationship(back_populates="baneos")


class ListaBlanca(SQLModel, table=True):
    __tablename__: ClassVar[str] = "lista_blanca"

    id: int | None = Field(default=None, primary_key=True)
    ip_o_red: str = Field(unique=True)
    descripcion: str | None = None
    predeterminada: bool = False


class Dispositivo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    token_fcm: str = Field(unique=True)
    plataforma: str
    alta: datetime = Field(default_factory=ahora_utc)
    actualizado_en: datetime = Field(default_factory=ahora_utc)
    usuario_id: int | None = Field(default=None, foreign_key="usuario.id")
    activo: bool = True


class Auditoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fecha_utc: datetime = Field(default_factory=ahora_utc)
    actor: str
    accion: str
    ip_afectada: str | None = None
    detalle: str | None = None
