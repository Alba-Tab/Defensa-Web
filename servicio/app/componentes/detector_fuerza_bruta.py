"""Observa los baneos que el jail de login ya decidió en Fail2ban."""

from app.componentes.actuador import ActuadorBloqueo


class DetectorFuerzaBruta:
    def __init__(self, jail_login: ActuadorBloqueo) -> None:
        self._jail_login = jail_login

    async def baneados(self) -> list[str]:
        return sorted(await self._jail_login.bloqueos())

    async def transferir(self, ip: str) -> None:
        """La liberación posterior usa el jail principal de la plataforma."""
        await self._jail_login.liberar(ip)
