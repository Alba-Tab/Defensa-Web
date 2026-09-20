import subprocess
from pathlib import Path
from typing import Literal, Protocol

EstadoComponente = Literal["activo", "inactivo", "no_aplica"]


class MonitorSuricata(Protocol):
    def estado(self) -> EstadoComponente: ...


class MonitorSuricataSimulado:
    def estado(self) -> EstadoComponente:
        return "no_aplica"


class MonitorSuricataSystemd:
    def __init__(
        self,
        systemctl: Path = Path("/usr/bin/systemctl"),
        servicio: str = "suricata",
        timeout_segundos: float = 2,
    ) -> None:
        self._systemctl = systemctl
        self._servicio = servicio
        self._timeout = timeout_segundos

    def estado(self) -> EstadoComponente:
        try:
            resultado = subprocess.run(
                [str(self._systemctl), "is-active", "--quiet", self._servicio],
                check=False,
                capture_output=True,
                timeout=self._timeout,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return "inactivo"
        return "activo" if resultado.returncode == 0 else "inactivo"
