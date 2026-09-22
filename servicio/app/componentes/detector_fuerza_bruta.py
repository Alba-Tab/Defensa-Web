"""Detector de intentos de fuerza bruta en access.log de nginx (Pb-17)."""

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
import re

from app.dominio.esquemas import EventoEntrada


class DetectorFuerzaBruta:
    """Detecta intentos fallidos de login en access.log de nginx.

    Lee POST /login con código 401 (Unauthorized) y agrupa por IP.
    Después de N intentos en una ventana temporal, genera un EventoEntrada.
    """

    def __init__(
        self,
        ruta_access_log: Path,
        umbral_intentos: int = 5,
        ventana_segundos: int = 600,
    ) -> None:
        self.ruta = ruta_access_log
        self.umbral = umbral_intentos
        self.ventana = timedelta(seconds=ventana_segundos)
        self._ultima_fecha = datetime.min.replace(tzinfo=UTC)

    async def procesar(self) -> list[EventoEntrada]:
        """Lee nuevo contenido de access.log y retorna eventos de fuerza bruta.

        Busca patrones: POST /login HTTP/1.1" 401|403
        Agrupa por IP origen.
        Después de N intentos en ventana T, genera EventoEntrada ficticio.
        """
        eventos = []

        try:
            if not self.ruta.exists():
                return eventos

            with open(self.ruta, "r", encoding="utf-8", errors="replace") as f:
                lineas = f.readlines()

            intentos_por_ip = defaultdict(list)
            # Patrón: IP ... "POST /login HTTP/x.x" 401|403
            patron = r'^(\d+\.\d+\.\d+\.\d+).*?"POST (/[^\s]*login[^\s]*) HTTP/[\d.]+"\s+(\d+)'

            for linea in lineas:
                match = re.match(patron, linea)
                if not match:
                    continue

                ip, path, codigo = match.groups()
                if codigo not in ("401", "403"):
                    continue

                fecha = self._parsear_timestamp(linea)
                if fecha is None:
                    continue

                intentos_por_ip[ip].append(fecha)

            ahora = datetime.now(UTC)
            for ip, intentos in intentos_por_ip.items():
                # Filtrar solo intentos dentro de la ventana y posteriores a última ejecución
                intentos_recientes = [
                    t for t in intentos
                    if (ahora - t) <= self.ventana and t > self._ultima_fecha
                ]

                if len(intentos_recientes) >= self.umbral:
                    ultima_fecha_intento = intentos_recientes[-1]
                    evento = EventoEntrada(
                        fecha_utc=ultima_fecha_intento,
                        ip_origen=ip,
                        sid=2000001,
                        firma="Intento de fuerza bruta detectado en /login",
                        categoria="brute_force",
                        severidad_firma=2,
                        accion="alerta",
                        url="/login",
                        metodo="POST",
                    )
                    eventos.append(evento)
                    self._ultima_fecha = max(self._ultima_fecha, ultima_fecha_intento)

        except Exception as e:
            import logging
            logging.getLogger(__name__).exception(f"Error procesando access.log: {e}")

        return eventos

    def _parsear_timestamp(self, linea_log: str) -> datetime | None:
        """Parsea timestamp de formato nginx: [22/Sep/2026:10:15:30 +0000]"""
        match = re.search(r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) ([+-]\d{4})\]', linea_log)
        if not match:
            return None

        dia, mes, anio, hora, minuto, segundo, zona = match.groups()

        meses = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
        }

        try:
            mes_num = meses.get(mes)
            if not mes_num:
                return None

            fecha = datetime(
                int(anio), mes_num, int(dia),
                int(hora), int(minuto), int(segundo),
                tzinfo=UTC
            )

            # Aplicar offset de zona horaria
            offset_horas = int(zona[:3])
            offset_minutos = int(zona[3:])
            offset = timedelta(hours=offset_horas, minutes=offset_minutos * (1 if offset_horas >= 0 else -1))
            fecha = fecha - offset  # Restar porque offset es relativo a UTC

            return fecha
        except (ValueError, KeyError):
            return None
