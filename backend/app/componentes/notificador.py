from pathlib import Path
from typing import Protocol

from app.dominio.modelos import Incidente


class Notificador(Protocol):
    async def enviar(self, incidente: Incidente, tokens: list[str]) -> set[str]: ...


class NotificadorNulo:
    async def enviar(self, incidente: Incidente, tokens: list[str]) -> set[str]:
        del incidente, tokens
        return set()


class NotificadorFirebase:
    def __init__(self, credenciales: Path) -> None:
        import firebase_admin  # type: ignore[import-untyped]
        from firebase_admin import credentials

        nombre = "defensa-web"
        try:
            self._app = firebase_admin.get_app(nombre)
        except ValueError:
            self._app = firebase_admin.initialize_app(
                credentials.Certificate(str(credenciales)), name=nombre
            )

    async def enviar(self, incidente: Incidente, tokens: list[str]) -> set[str]:
        if not tokens:
            return set()

        import asyncio

        from firebase_admin import messaging

        mensaje = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=f"Incidente de severidad {incidente.severidad}",
                body=f"{incidente.tipo_ataque} desde {incidente.ip_origen}",
            ),
            data={"incidente_id": str(incidente.id)},
            tokens=tokens[:500],
        )
        respuesta = await asyncio.to_thread(
            messaging.send_each_for_multicast, mensaje, app=self._app
        )
        invalidos: set[str] = set()
        for token, resultado in zip(tokens, respuesta.responses, strict=False):
            if not resultado.success and "UNREGISTERED" in str(resultado.exception).upper():
                invalidos.add(token)
        return invalidos
