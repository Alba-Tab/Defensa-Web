import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

from app.componentes.estado_componentes import MonitorSuricataSystemd


def test_monitor_suricata_informa_activo() -> None:
    monitor = MonitorSuricataSystemd(Path("/usr/bin/systemctl"))
    with patch("app.componentes.estado_componentes.subprocess.run") as ejecutar:
        ejecutar.return_value = Mock(returncode=0)

        assert monitor.estado() == "activo"

    ejecutar.assert_called_once_with(
        ["/usr/bin/systemctl", "is-active", "--quiet", "suricata"],
        check=False,
        capture_output=True,
        timeout=2,
    )


def test_monitor_suricata_informa_inactivo_ante_fallo_o_timeout() -> None:
    monitor = MonitorSuricataSystemd(Path("/usr/bin/systemctl"))
    with patch(
        "app.componentes.estado_componentes.subprocess.run",
        side_effect=subprocess.TimeoutExpired("systemctl", 2),
    ):
        assert monitor.estado() == "inactivo"
