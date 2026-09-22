import json
import shutil
import subprocess
from pathlib import Path

import pytest
from scapy.all import IP, TCP, Ether, Raw, wrpcap

RAIZ = Path(__file__).resolve().parents[2]
REGLAS = RAIZ / "infra" / "suricata" / "local.rules"


def _configuracion_suricata() -> Path | None:
    candidatas = (
        Path("/etc/suricata/suricata.yaml"),
        Path("/opt/homebrew/etc/suricata/suricata.yaml"),
    )
    return next((ruta for ruta in candidatas if ruta.exists()), None)


def _flujo_http(ip: str, puerto: int, uri: str, desplazamiento: int) -> list[Ether]:
    servidor = "198.51.100.20"
    secuencia_cliente = 1000 + desplazamiento
    secuencia_servidor = 9000 + desplazamiento
    peticion = (
        f"GET {uri} HTTP/1.1\r\n"
        "Host: app.lab\r\n"
        "User-Agent: prueba-pb2\r\n"
        "Connection: close\r\n\r\n"
    ).encode()
    ethernet = Ether(src="02:00:00:00:00:10", dst="02:00:00:00:00:20")
    ethernet_respuesta = Ether(src="02:00:00:00:00:20", dst="02:00:00:00:00:10")
    return [
        ethernet
        / IP(src=ip, dst=servidor)
        / TCP(sport=puerto, dport=80, flags="S", seq=secuencia_cliente),
        ethernet_respuesta
        / IP(src=servidor, dst=ip)
        / TCP(
            sport=80,
            dport=puerto,
            flags="SA",
            seq=secuencia_servidor,
            ack=secuencia_cliente + 1,
        ),
        ethernet
        / IP(src=ip, dst=servidor)
        / TCP(
            sport=puerto,
            dport=80,
            flags="A",
            seq=secuencia_cliente + 1,
            ack=secuencia_servidor + 1,
        ),
        ethernet
        / IP(src=ip, dst=servidor)
        / TCP(
            sport=puerto,
            dport=80,
            flags="PA",
            seq=secuencia_cliente + 1,
            ack=secuencia_servidor + 1,
        )
        / Raw(peticion),
    ]


def test_suricata_detecta_sqli_y_no_marca_navegacion_legitima(tmp_path: Path) -> None:
    binario = shutil.which("suricata")
    configuracion = _configuracion_suricata()
    if binario is None or configuracion is None:
        pytest.skip("Suricata no está instalado en este equipo")

    pcap = tmp_path / "trafico.pcap"
    salida = tmp_path / "salida"
    salida.mkdir()
    paquetes = _flujo_http("192.0.2.10", 12345, "/buscar?q=1%27%20OR%201%3D1--", 0) + _flujo_http(
        "192.0.2.11", 12346, "/buscar?q=teclado", 100
    )
    wrpcap(str(pcap), paquetes)

    subprocess.run(
        [
            binario,
            "--simulate-ips",
            "-r",
            str(pcap),
            "-l",
            str(salida),
            "-c",
            str(configuracion),
            "-S",
            str(REGLAS),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    eventos = [
        json.loads(linea)
        for linea in (salida / "eve.json").read_text(encoding="utf-8").splitlines()
    ]
    alertas = [evento for evento in eventos if evento.get("event_type") == "alert"]

    assert len(alertas) == 1
    alerta = alertas[0]
    assert alerta["src_ip"] == "192.0.2.10"
    assert alerta["alert"]["signature_id"] == 1000001
    assert alerta["alert"]["signature"] == "DEFENSA SQLi de alta confianza"
    assert alerta["alert"]["category"] == "Web Application Attack"
    assert alerta["alert"]["severity"] == 1
    assert alerta["alert"]["action"] == "blocked"
    assert alerta["http"]["http_method"] == "GET"
    assert alerta["http"]["url"] == "/buscar?q=1%27%20OR%201%3D1--"
    assert not any(evento.get("src_ip") == "192.0.2.11" for evento in alertas)


def test_suricata_detecta_xss_script_tag(tmp_path: Path) -> None:
    """Pb-11: Verifica que Suricata detecta XSS con script tag (SID 1000005)"""
    binario = shutil.which("suricata")
    configuracion = _configuracion_suricata()
    if binario is None or configuracion is None:
        pytest.skip("Suricata no está instalado en este equipo")

    pcap = tmp_path / "trafico.pcap"
    salida = tmp_path / "salida"
    salida.mkdir()
    paquetes = _flujo_http("192.0.2.20", 12347, "/search?q=%3Cscript%3Ealert(1)%3C/script%3E", 0) + _flujo_http(
        "192.0.2.21", 12348, "/search?q=keyboard", 100
    )
    wrpcap(str(pcap), paquetes)

    subprocess.run(
        [
            binario,
            "--simulate-ips",
            "-r",
            str(pcap),
            "-l",
            str(salida),
            "-c",
            str(configuracion),
            "-S",
            str(REGLAS),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    eventos = [
        json.loads(linea)
        for linea in (salida / "eve.json").read_text(encoding="utf-8").splitlines()
    ]
    alertas = [evento for evento in eventos if evento.get("event_type") == "alert"]

    assert len(alertas) == 1
    alerta = alertas[0]
    assert alerta["src_ip"] == "192.0.2.20"
    assert alerta["alert"]["signature_id"] == 1000005
    assert "XSS" in alerta["alert"]["signature"]
    assert alerta["alert"]["category"] == "Web Application Attack"
    assert alerta["http"]["http_method"] == "GET"
    assert not any(evento.get("src_ip") == "192.0.2.21" for evento in alertas)


def test_suricata_detecta_path_traversal(tmp_path: Path) -> None:
    """Pb-12: Verifica que Suricata detecta path traversal (SID 1000008-1000010)"""
    binario = shutil.which("suricata")
    configuracion = _configuracion_suricata()
    if binario is None or configuracion is None:
        pytest.skip("Suricata no está instalado en este equipo")

    pcap = tmp_path / "trafico.pcap"
    salida = tmp_path / "salida"
    salida.mkdir()
    paquetes = _flujo_http("192.0.2.30", 12349, "/download?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd", 0) + _flujo_http(
        "192.0.2.31", 12350, "/download?file=documento.pdf", 100
    )
    wrpcap(str(pcap), paquetes)

    subprocess.run(
        [
            binario,
            "--simulate-ips",
            "-r",
            str(pcap),
            "-l",
            str(salida),
            "-c",
            str(configuracion),
            "-S",
            str(REGLAS),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    eventos = [
        json.loads(linea)
        for linea in (salida / "eve.json").read_text(encoding="utf-8").splitlines()
    ]
    alertas = [evento for evento in eventos if evento.get("event_type") == "alert"]

    assert len(alertas) >= 1
    traversal_alerts = [a for a in alertas if a["alert"]["signature_id"] in [1000008, 1000009, 1000010]]
    assert len(traversal_alerts) >= 1
    alerta = traversal_alerts[0]
    assert alerta["src_ip"] == "192.0.2.30"
    assert "path traversal" in alerta["alert"]["signature"].lower()
    assert alerta["alert"]["category"] == "Web Application Attack"
    assert alerta["http"]["http_method"] == "GET"
    assert not any(evento.get("src_ip") == "192.0.2.31" for evento in alertas)
