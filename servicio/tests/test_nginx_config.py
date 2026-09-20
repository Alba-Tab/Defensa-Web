from pathlib import Path

CONFIGURACION = (
    Path(__file__).resolve().parents[2] / "infra" / "nginx" / "defensa-web.conf"
).read_text(encoding="utf-8")


def test_pb15_limita_por_ip_real_y_responde_429() -> None:
    assert "limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;" in CONFIGURACION
    assert "limit_req zone=general burst=20 nodelay;" in CONFIGURACION
    assert "limit_req_status 429;" in CONFIGURACION
    assert "real_ip_header X-Forwarded-For;" in CONFIGURACION
    assert "real_ip_recursive on;" in CONFIGURACION
    assert "set_real_ip_from 127.0.0.1;" in CONFIGURACION


def test_pb15_aplica_limite_especial_al_login() -> None:
    assert "limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;" in CONFIGURACION
    inicio = CONFIGURACION.index("location = /rest/user/login")
    fin = CONFIGURACION.index("\n    }", inicio)
    bloque_login = CONFIGURACION[inicio:fin]

    assert "limit_req zone=general burst=20 nodelay;" in bloque_login
    assert "limit_req zone=login burst=4 nodelay;" in bloque_login
    assert "proxy_pass http://127.0.0.1:3000;" in bloque_login
