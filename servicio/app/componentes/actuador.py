import asyncio
from datetime import datetime
from ipaddress import ip_address
from pathlib import Path
from re import fullmatch
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


class Fail2banActuator:
    def __init__(self, binario: Path, jail: str, *, usar_sudo: bool = True) -> None:
        if fullmatch(r"[A-Za-z0-9_-]+", jail) is None:
            raise ValueError("Nombre de jail inválido")
        self._binario = str(binario)
        self._jail = jail
        self._prefijo = ("/usr/bin/sudo", "-n") if usar_sudo else ()

    async def _ejecutar(self, *argumentos: str) -> str:
        proceso = await asyncio.create_subprocess_exec(
            *self._prefijo,
            self._binario,
            *argumentos,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        salida, error = await proceso.communicate()
        if proceso.returncode != 0:
            mensaje = error.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"Fail2ban rechazó la operación: {mensaje}")
        return salida.decode("utf-8", errors="replace").strip()

    async def bloquear(self, ip: str, expira: datetime) -> None:
        del expira  # La duración está configurada en el jail.
        ip_canonica = str(ip_address(ip))
        if ip_canonica not in await self.bloqueos():
            await self._ejecutar("set", self._jail, "banip", ip_canonica)

    async def liberar(self, ip: str) -> None:
        ip_canonica = str(ip_address(ip))
        if ip_canonica in await self.bloqueos():
            await self._ejecutar("set", self._jail, "unbanip", ip_canonica)

    async def bloqueos(self) -> dict[str, datetime]:
        salida = await self._ejecutar("get", self._jail, "banip")
        ahora = datetime.now()
        return {str(ip_address(valor)): ahora for valor in salida.split() if valor.strip()}
