"""Consulta la lista blanca dinámica antes de que Fail2ban decida un baneo."""

import ipaddress
import sqlite3
import sys


def ignorar(ip: str, db: str) -> bool:
    origen = ipaddress.ip_address(ip)
    try:
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=2) as conexion:
            entradas = conexion.execute("SELECT ip_o_red FROM lista_blanca").fetchall()
    except sqlite3.Error:
        # Sin base no hay decisión segura: se omite el baneo hasta recuperarla.
        return True
    return any(origen in ipaddress.ip_network(red, strict=False) for (red,) in entradas)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(2)
    try:
        raise SystemExit(0 if ignorar(sys.argv[1], sys.argv[2]) else 1)
    except ValueError:
        raise SystemExit(0) from None
