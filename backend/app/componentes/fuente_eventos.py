import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import unquote, unquote_plus, urlsplit

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
            url = http.get("url")
            partes = urlsplit(str(url)) if url else None
            cuerpo = http.get("request_body") or dato.get("http_request_body")
            return EventoEntrada(
                fecha_utc=datetime.fromisoformat(dato["timestamp"].replace("Z", "+00:00")),
                ip_origen=dato["src_ip"],
                sid=int(alerta["signature_id"]),
                firma=str(alerta["signature"]),
                categoria=str(alerta.get("category", "sin_categoria")),
                severidad_firma=int(alerta.get("severity", 3)),
                accion="descarte" if alerta.get("action") == "blocked" else "alerta",
                metodo=http.get("http_method"),
                url=url,
                uri_decodificada=unquote(partes.path) if partes else None,
                parametros=unquote_plus(partes.query) if partes and partes.query else None,
                cuerpo_fragmento=str(cuerpo)[:2048] if cuerpo else None,
                user_agent=http.get("http_user_agent"),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

    async def eventos(self) -> AsyncIterator[EventoEntrada]:
        archivo = None
        inode: int | None = None
        primera_apertura = True
        while True:
            try:
                if archivo is None:
                    estado = self._ruta.stat()
                    archivo = self._ruta.open(encoding="utf-8")
                    if primera_apertura:
                        archivo.seek(0, 2)
                        primera_apertura = False
                    inode = estado.st_ino

                linea = archivo.readline()
                if linea:
                    evento = self._convertir(linea)
                    if evento is not None:
                        yield evento
                    continue

                # Se drena primero el archivo anterior. Solo al llegar a EOF se
                # cambia al nuevo inode, empezando desde byte cero para no perder
                # líneas escritas entre el rename de logrotate y este sondeo.
                estado_actual = self._ruta.stat()
                if inode != estado_actual.st_ino:
                    archivo.close()
                    archivo = self._ruta.open(encoding="utf-8")
                    inode = estado_actual.st_ino
                    continue
                await asyncio.sleep(self._intervalo)
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
