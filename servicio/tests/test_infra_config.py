from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def leer(ruta: str) -> str:
    return (RAIZ / ruta).read_text(encoding="utf-8")


def test_nftables_no_elimina_reglas_de_docker_ni_fail2ban() -> None:
    configuracion = leer("infra/nftables/defensa.nft")

    instrucciones = [
        linea.strip()
        for linea in configuracion.splitlines()
        if linea.strip() and not linea.lstrip().startswith("#")
    ]
    assert "flush ruleset" not in instrucciones
    assert "destroy table inet defensa" in configuracion


def test_suricata_se_ejecuta_en_primer_plano_bajo_systemd() -> None:
    unidad = leer("infra/systemd/suricata-nfq.conf")

    assert "Type=simple" in unidad
    assert "ExecStart=/usr/bin/suricata -q 0" in unidad


def test_servicio_defensa_permite_el_sudo_restringido_del_actuador() -> None:
    unidad = leer("infra/systemd/defensa.service")
    sudoers = leer("infra/sudoers/defensa")

    assert "NoNewPrivileges=true" not in unidad
    assert "/usr/bin/fail2ban-client get defensa-web banip" in sudoers


def test_healthcheck_usa_el_node_disponible_en_juice_shop() -> None:
    compose = leer("infra/compose/app-protegida.yaml")

    assert '"/nodejs/bin/node"' in compose
    assert "start_period: 20s" in compose


def test_aprovisionamiento_reinicia_servicios_y_espera_salud() -> None:
    provision = leer("infra/provision/provision.sh")

    for servicio in ("nftables", "docker", "fail2ban", "suricata", "nginx", "defensa"):
        assert f"systemctl restart {servicio}" in provision
    assert "up -d --wait --wait-timeout 180" in provision


def test_verificacion_cubre_estado_real_y_permisos() -> None:
    verificacion = leer("infra/verificar.sh")

    assert "systemctl is-active --quiet suricata" in verificacion
    assert 'docker inspect -f "{{.State.Health.Status}}"' in verificacion
    assert "sudo -u defensa sudo -n" in verificacion
