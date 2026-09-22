"""Comprobación no destructiva de Pb-18 en la VM aprovisionada.

Ejecutar: vagrant ssh -c 'sudo /opt/defensa/venv/bin/python /vagrant/pruebas/verificar_pb18_vm.py'
No imprime contraseña ni token. La entrada de prueba se elimina al terminar.
"""

import sqlite3
from pathlib import Path

import httpx


def leer_ajustes() -> dict[str, str]:
    ajustes = {}
    for linea in (
        Path("/etc/defensa/defensa.env").read_text(encoding="utf-8").splitlines()
    ):
        if linea and not linea.lstrip().startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            ajustes[clave.strip()] = valor.strip().strip('"')
    return ajustes


def main() -> None:
    ajustes = leer_ajustes()
    assert ajustes["DEFENSA_MODO"] == "real"
    red_prueba = "203.0.113.254/32"
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=30) as cliente:
        inicio = cliente.post(
            "/api/auth/login",
            json={
                "usuario": ajustes["DEFENSA_ADMIN_USUARIO"],
                "contrasena": ajustes["DEFENSA_ADMIN_PASSWORD"],
            },
        )
        assert inicio.status_code == 200, f"Login: HTTP {inicio.status_code}"
        cliente.headers["Authorization"] = f"Bearer {inicio.json()['access_token']}"

        inicial = cliente.get("/api/lista-blanca")
        assert inicial.status_code == 200
        entradas = inicial.json()
        assert any(
            item["ip_o_red"] == "127.0.0.0/8" and item["predeterminada"]
            for item in entradas
        )
        assert not any(item["ip_o_red"] == red_prueba for item in entradas), (
            "La red reservada para la prueba ya existe; no se modificó"
        )
        protegida = next(item for item in entradas if item["ip_o_red"] == "127.0.0.0/8")
        assert cliente.delete(f"/api/lista-blanca/{protegida['id']}").status_code == 403
        assert (
            cliente.post("/api/lista-blanca", json={"ip_o_red": "no-es-ip"}).status_code
            == 422
        )

        creada_id = None
        try:
            alta = cliente.post(
                "/api/lista-blanca",
                json={"ip_o_red": red_prueba, "descripcion": "Comprobación Pb-18 VM"},
            )
            assert alta.status_code == 201, f"Alta: HTTP {alta.status_code}"
            creada_id = alta.json()["id"]
            assert alta.json()["predeterminada"] is False
            assert (
                cliente.post(
                    "/api/lista-blanca", json={"ip_o_red": red_prueba}
                ).status_code
                == 409
            )
        finally:
            if creada_id is not None:
                baja = cliente.delete(f"/api/lista-blanca/{creada_id}")
                assert baja.status_code == 200, f"Baja: HTTP {baja.status_code}"

    ruta_bd = ajustes["DEFENSA_DATABASE_URL"].removeprefix("sqlite:///")
    with sqlite3.connect(ruta_bd) as conexion:
        registros = conexion.execute(
            "SELECT actor, accion, ip_afectada FROM auditoria "
            "WHERE ip_afectada = ? ORDER BY id DESC LIMIT 2",
            (red_prueba,),
        ).fetchall()
    assert registros == [
        (ajustes["DEFENSA_ADMIN_USUARIO"], "lista_blanca_baja", red_prueba),
        (ajustes["DEFENSA_ADMIN_USUARIO"], "lista_blanca_alta", red_prueba),
    ]
    print(
        "OK Pb-18: autenticación, consulta, protección, validación, alta, baja y auditoría"
    )


if __name__ == "__main__":
    main()
