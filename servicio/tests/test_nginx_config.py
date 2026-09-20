import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
CONFIGURACION = (RAIZ / "infra" / "nginx" / "defensa-web.conf").read_text(encoding="utf-8")
NFTABLES = (RAIZ / "infra" / "nftables" / "defensa.nft").read_text(encoding="utf-8")
SURICATA_SYSTEMD = (RAIZ / "infra" / "systemd" / "suricata-nfq.conf").read_text(encoding="utf-8")


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


def test_pb29_redirige_http_y_termina_tls() -> None:
    assert "listen 80 default_server;" in CONFIGURACION
    assert "return 308 https://$host$request_uri;" in CONFIGURACION
    assert "listen 443 ssl http2 default_server;" in CONFIGURACION
    assert "ssl_certificate /etc/defensa/tls/defensa-web.crt;" in CONFIGURACION
    assert "ssl_certificate_key /etc/defensa/tls/defensa-web.key;" in CONFIGURACION
    assert "ssl_protocols TLSv1.2 TLSv1.3;" in CONFIGURACION


def test_pb29_inspecciona_el_tramo_http_descifrado() -> None:
    assert "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;" in CONFIGURACION
    assert 'oifname "lo" tcp dport 3000 queue num 0 bypass' in NFTABLES
    assert 'oifname "lo" tcp sport 3000 queue num 0 bypass' in NFTABLES
    assert "outputs.1.eve-log.xff.enabled=yes" in SURICATA_SYSTEMD
    assert "outputs.1.eve-log.xff.mode=overwrite" in SURICATA_SYSTEMD
    assert "outputs.1.eve-log.xff.deployment=reverse" in SURICATA_SYSTEMD
    assert "outputs.1.eve-log.xff.header=X-Forwarded-For" in SURICATA_SYSTEMD


def test_pb29_no_versiona_certificados_ni_claves() -> None:
    resultado = subprocess.run(
        ["git", "ls-files", "*.crt", "*.key", "*.pem"],
        cwd=RAIZ,
        check=True,
        capture_output=True,
        text=True,
    )
    assert resultado.stdout.strip() == ""


def test_pb29_genera_certificado_de_laboratorio(tmp_path: Path) -> None:
    if shutil.which("openssl") is None:
        pytest.skip("openssl no está disponible")

    script = RAIZ / "infra" / "nginx" / "generar-certificado-lab.sh"
    entorno = os.environ.copy()
    entorno.update(
        {
            "DEFENSA_TLS_DIR": str(tmp_path),
            "DEFENSA_TLS_IP": "192.168.56.20",
            "DEFENSA_TLS_DNS": "defensa-web.local",
            "DEFENSA_TLS_PERMITIR_USUARIO": "SI",
        }
    )
    subprocess.run([str(script)], check=True, env=entorno, capture_output=True, text=True)

    certificado = tmp_path / "defensa-web.crt"
    clave = tmp_path / "defensa-web.key"
    assert certificado.is_file()
    assert clave.is_file()
    assert stat.S_IMODE(clave.stat().st_mode) == 0o600
    detalles = subprocess.run(
        ["openssl", "x509", "-in", str(certificado), "-noout", "-text"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "DNS:defensa-web.local" in detalles
    assert "IP Address:192.168.56.20" in detalles
