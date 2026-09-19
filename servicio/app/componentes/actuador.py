from datetime import datetime
from typing import Protocol


class ActuadorBloqueo(Protocol):
    async def bloquear(self, ip: str, expira: datetime) -> None: ...

    async def liberar(self, ip: str) -> None: ...

    async def bloqueos(self) -> dict[str, datetime]: ...


class DryRunActuator:
    """Actuador determinista que no ejecuta comandos ni modifica el firewall."""

    def __init__(self) -> None:
        self._bloqueos: dict[str, datetime] = {}

    async def bloquear(self, ip: str, expira: datetime) -> None:
        self._bloqueos[ip] = expira

    async def liberar(self, ip: str) -> None:
        self._bloqueos.pop(ip, None)

    async def bloqueos(self) -> dict[str, datetime]:
        return dict(self._bloqueos)
