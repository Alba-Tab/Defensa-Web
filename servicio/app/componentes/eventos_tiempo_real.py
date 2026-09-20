from asyncio import Queue, QueueFull
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AlertaIncidente:
    incidente_id: int
    tipo_ataque: str
    severidad: int
    ip_origen: str

    def como_dict(self) -> dict[str, str | int]:
        return asdict(self)


class BusEventos:
    def __init__(self) -> None:
        self._suscriptores: set[Queue[AlertaIncidente]] = set()

    @asynccontextmanager
    async def suscribir(self) -> AsyncIterator[Queue[AlertaIncidente]]:
        cola: Queue[AlertaIncidente] = Queue(maxsize=100)
        self._suscriptores.add(cola)
        try:
            yield cola
        finally:
            self._suscriptores.discard(cola)

    def publicar(self, alerta: AlertaIncidente) -> None:
        for cola in tuple(self._suscriptores):
            try:
                cola.put_nowait(alerta)
            except QueueFull:
                _ = cola.get_nowait()
                cola.task_done()
                cola.put_nowait(alerta)
