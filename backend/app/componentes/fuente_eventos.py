import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path
from typing import Protocol

from app.dominio.esquemas import EventoEntrada


class FuenteEventos(Protocol):
    def eventos(self) -> AsyncIterator[EventoEntrada]: ...


class FakeSource:
    def __init__(self) -> None:
        self._cola: asyncio.Queue[EventoEntrada] = asyncio.Queue(maxsize=1000)

    async def publicar(self, evento: EventoEntrada) -> None:
        await self._cola.put(evento)

    async def eventos(self) -> AsyncIterator[EventoEntrada]:
        while True:
            yield await self._cola.get()


class EveSource:
    """Sigue eve.json y reabre el archivo cuando Suricata lo rota."""

    def __init__(self, ruta: Path, intervalo_segundos: float = 0.2) -> None:
        self._ruta = ruta
        self._intervalo = intervalo_segundos

    @staticmethod
    def _convertir(linea: str) -> EventoEntrada | None:
        try:
            dato = json.loads(linea)
            if dato.get("event_type") != "alert":
                return None
            alerta = dato["alert"]
            http = dato.get("http", {})
            return EventoEntrada(
                fecha_utc=datetime.fromisoformat(dato["timestamp"].replace("Z", "+00:00")),
                ip_origen=dato["src_ip"],
                sid=int(alerta["signature_id"]),
                firma=str(alerta["signature"]),
                categoria=str(alerta.get("category", "sin_categoria")),
                severidad_firma=int(alerta.get("severity", 3)),
                metodo=http.get("http_method"),
                url=http.get("url"),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

    async def eventos(self) -> AsyncIterator[EventoEntrada]:
        archivo = None
        inode: int | None = None
        while True:
            try:
                estado = self._ruta.stat()
                if archivo is None or inode != estado.st_ino:
                    if archivo is not None:
                        archivo.close()
                    archivo = self._ruta.open(encoding="utf-8")
                    archivo.seek(0, 2)
                    inode = estado.st_ino

                linea = archivo.readline()
                if not linea:
                    await asyncio.sleep(self._intervalo)
                    continue
                evento = self._convertir(linea)
                if evento is not None:
                    yield evento
            except FileNotFoundError:
                if archivo is not None:
                    archivo.close()
                    archivo = None
                    inode = None
                await asyncio.sleep(self._intervalo)
            except asyncio.CancelledError:
                if archivo is not None:
                    archivo.close()
                raise
