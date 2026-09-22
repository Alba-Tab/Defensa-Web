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


def _flujo_http(
    ip: str, puerto: int, uri: str, desplazamiento: int, user_agent: str = "prueba-pb2"
) -> list[Ether]:
    servidor = "198.51.100.20"
    secuencia_cliente = 1000 + desplazamiento
    secuencia_servidor = 9000 + desplazamiento
    peticion = (
        f"GET {uri} HTTP/1.1\r\n"
        "Host: app.lab\r\n"
        f"User-Agent: {user_agent}\r\n"
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


def test_suricata_detecta_sondeo_y_escaneo_sin_marcar_paginacion(tmp_path: Path) -> None:
    binario = shutil.which("suricata")
    configuracion = _configuracion_suricata()
    if binario is None or configuracion is None:
        pytest.skip("Suricata no está instalado en este equipo")

    pcap = tmp_path / "trafico-hu.pcap"
    salida = tmp_path / "salida-hu"
    salida.mkdir()
    paquetes = (
        _flujo_http("192.0.2.21", 12351, "/.env", 0)
        + _flujo_http("192.0.2.22", 12352, "/settings.yml.bak", 100)
        + _flujo_http("192.0.2.23", 12353, "/admin", 200, "Nikto/2.5")
        + _flujo_http("192.0.2.25", 12355, "/unknown", 400, "Fuzz Faster U Fool v2.1.0")
    )
    for indice in range(20):
        paquetes += _flujo_http(
            "192.0.2.24",
            13000 + indice,
            f"/products?page={indice}",
            500 + indice * 100,
            "Mozilla/5.0",
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
    alertas = [
        evento
        for linea in (salida / "eve.json").read_text(encoding="utf-8").splitlines()
        if (evento := json.loads(linea)).get("event_type") == "alert"
    ]

    assert {(alerta["src_ip"], alerta["alert"]["signature_id"]) for alerta in alertas} == {
        ("192.0.2.21", 1000002),
        ("192.0.2.22", 1000003),
        ("192.0.2.23", 1000004),
        ("192.0.2.25", 1000004),
    }
