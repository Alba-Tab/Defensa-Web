"""Prueba controlada de Pb-17 en la VM; solo usa una IP TEST-NET reservada."""

import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

import httpx

IP_PRUEBA = "198.51.100.42"
BASE = Path("/etc/defensa/defensa.env")
BD = Path("/opt/defensa/datos/defensa.db")


def ajustes() -> dict[str, str]:
    valores = {}
    for linea in BASE.read_text(encoding="utf-8").splitlines():
        if linea and not linea.lstrip().startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip().strip('"')
    return valores


def baneo() -> tuple[int, str, int, str, str | None, str, str, int] | None:
    with sqlite3.connect(BD) as conexion:
        return conexion.execute(
            "SELECT b.id,b.estado,b.nivel_reincidencia,i.tipo_ataque,i.origen_informe,"
            "b.inicio,b.expira,i.severidad "
            "FROM baneo b JOIN incidente i ON i.id=b.incidente_id "
            "WHERE b.ip=? ORDER BY b.id DESC LIMIT 1",
            (IP_PRUEBA,),
        ).fetchone()


def ips(jail: str) -> str:
    return subprocess.check_output(
        ["fail2ban-client", "get", jail, "banip"], text=True
    ).strip()


def main() -> None:
    existente = baneo()
    nivel_esperado = existente[2] + 1 if existente and existente[1] != "vigente" else 0
    if existente is None or existente[1] != "vigente":
        assert IP_PRUEBA not in ips("defensa-web")
        for _ in range(5):
            subprocess.run(
                ["fail2ban-client", "set", "defensa-login", "attempt", IP_PRUEBA],
                check=True,
                capture_output=True,
                text=True,
            )
        for _ in range(60):
            existente = baneo()
            if (
                existente
                and existente[1] == "vigente"
                and IP_PRUEBA in ips("defensa-web")
            ):
                break
            time.sleep(1)
    assert existente is not None and existente[1] == "vigente"
    assert existente[3] == "fuerza_bruta"
    assert existente[2] == nivel_esperado
    segundos = min(600 * 2**nivel_esperado, 86400)
    assert datetime.fromisoformat(existente[6]) - datetime.fromisoformat(
        existente[5]
    ) == timedelta(seconds=segundos)
    assert existente[7] == (4 if nivel_esperado else 3)
    assert IP_PRUEBA in ips("defensa-web")
    assert IP_PRUEBA not in ips("defensa-login")

    configuracion = ajustes()
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=20) as cliente:
        acceso = cliente.post(
            "/api/auth/login",
            json={
                "usuario": configuracion["DEFENSA_ADMIN_USUARIO"],
                "contrasena": configuracion["DEFENSA_ADMIN_PASSWORD"],
            },
        )
        assert acceso.status_code == 200, f"Login HTTP {acceso.status_code}"
        cliente.headers["Authorization"] = f"Bearer {acceso.json()['access_token']}"
        liberacion = cliente.post(f"/api/baneos/{IP_PRUEBA}/liberar")
        assert liberacion.status_code == 200, (
            f"Liberación HTTP {liberacion.status_code}"
        )

    assert baneo() is not None and baneo()[1] == "liberado"
    assert IP_PRUEBA not in ips("defensa-web")
    print("OK Pb-17: Fail2ban, incidente, baneo y liberación autenticada")


if __name__ == "__main__":
    main()
