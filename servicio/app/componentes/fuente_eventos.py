import asyncio
from collections.abc import AsyncIterator
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
