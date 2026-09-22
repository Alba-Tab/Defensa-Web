import importlib.util
import re
import sqlite3
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "infra" / "fail2ban" / "ignorar_ip.py"
JAIL = RAIZ / "infra" / "fail2ban" / "jail.local"
FILTRO = RAIZ / "infra" / "fail2ban" / "defensa-login.conf"


def test_jail_exige_cinco_fallos_en_sesenta_segundos() -> None:
    jail = JAIL.read_text(encoding="utf-8").split("[defensa-login]", maxsplit=1)[1]
    assert "maxretry = 5" in jail
    assert "findtime = 60" in jail
    assert "logpath = /var/log/defensa/access.log" in jail
    assert "ignorecommand = " in jail
    filtro = FILTRO.read_text(encoding="utf-8")
    assert "path=/api/auth/login status=(?:401|403)" in filtro


def test_ignorecommand_consulta_redes_dinamicas_y_falla_seguro(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("ignorar_ip", SCRIPT)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    base = tmp_path / "defensa.db"
    with sqlite3.connect(base) as conexion:
        conexion.execute("CREATE TABLE lista_blanca (ip_o_red TEXT NOT NULL)")
        conexion.execute("INSERT INTO lista_blanca VALUES ('198.51.100.0/24')")
    assert modulo.ignorar("198.51.100.42", str(base))
    assert not modulo.ignorar("203.0.113.42", str(base))
    assert modulo.ignorar("203.0.113.42", str(tmp_path / "sin-base.db"))


@pytest.mark.parametrize(
    ("status", "coincide"), [("401", True), ("403", True), ("200", False), ("429", False)]
)
def test_filtro_acepta_solo_respuestas_fallidas(status: str, coincide: bool) -> None:
    linea = next(
        linea
        for linea in FILTRO.read_text(encoding="utf-8").splitlines()
        if linea.startswith("failregex = ")
    )
    patron = linea.split(" = ", maxsplit=1)[1].replace("<HOST>", r"(?:\d{1,3}\.){3}\d{1,3}")
    log = f" DEFENSA_LOGIN ip=192.0.2.42 method=POST path=/api/auth/login status={status}"
    assert bool(re.match(patron, log)) is coincide
