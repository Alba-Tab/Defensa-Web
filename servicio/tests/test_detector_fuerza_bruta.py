"""Tests para DetectorFuerzaBruta (Pb-17)."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
import tempfile

import pytest

from app.componentes.detector_fuerza_bruta import DetectorFuerzaBruta


@pytest.mark.asyncio
async def test_detecta_intentos_fallidos_login() -> None:
    """Pb-17: Verificar que detecta POST /login con código 401."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        ruta = Path(f.name)
        ahora = datetime.now(UTC)
        fecha_str = ahora.strftime("%d/%b/%Y:%H:%M:%S +0000")

        lineas = [
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.200 - - [{fecha_str}] "GET / HTTP/1.1" 200 512 "-" "curl/8.5.0"\n',
        ]

        f.writelines(lineas)
        f.flush()

    try:
        detector = DetectorFuerzaBruta(ruta, umbral_intentos=5)
        eventos = await detector.procesar()

        assert len(eventos) == 1, f"Se esperaba 1 evento, se obtuvieron {len(eventos)}"

        evento = eventos[0]
        assert evento.ip_origen == "192.168.1.100"
        assert evento.categoria == "brute_force"
        assert evento.severidad_firma == 2
        assert evento.sid == 2000001
        assert evento.firma == "Intento de fuerza bruta detectado en /login"
        assert evento.metodo == "POST"
        assert evento.url == "/login"
        assert evento.accion == "alerta"
    finally:
        ruta.unlink()


@pytest.mark.asyncio
async def test_agrupa_por_ip() -> None:
    """Pb-17: Verificar que agrupa intentos por IP origen."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        ruta = Path(f.name)
        ahora = datetime.now(UTC)
        fecha_str = ahora.strftime("%d/%b/%Y:%H:%M:%S +0000")

        lineas = []
        # IP 1: 5 intentos (debe detectarse)
        for _ in range(5):
            lineas.append(f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n')

        # IP 2: 3 intentos (no alcanza umbral)
        for _ in range(3):
            lineas.append(f'192.168.1.200 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n')

        # IP 3: 5 intentos (debe detectarse)
        for _ in range(5):
            lineas.append(f'192.168.1.250 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n')

        f.writelines(lineas)
        f.flush()

    try:
        detector = DetectorFuerzaBruta(ruta, umbral_intentos=5)
        eventos = await detector.procesar()

        assert len(eventos) == 2, f"Se esperaba 2 eventos, se obtuvieron {len(eventos)}"

        ips = {evento.ip_origen for evento in eventos}
        assert ips == {"192.168.1.100", "192.168.1.250"}
    finally:
        ruta.unlink()


@pytest.mark.asyncio
async def test_respeta_ventana_temporal() -> None:
    """Pb-17: Verificar que solo cuenta intentos dentro de la ventana."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        ruta = Path(f.name)
        ahora = datetime.now(UTC)
        hace_20_min = ahora - timedelta(minutes=20)

        fecha_ahora = ahora.strftime("%d/%b/%Y:%H:%M:%S +0000")
        fecha_antigua = hace_20_min.strftime("%d/%b/%Y:%H:%M:%S +0000")

        lineas = [
            # 3 intentos hace 20 minutos (fuera de ventana de 10 min)
            f'192.168.1.100 - - [{fecha_antigua}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_antigua}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_antigua}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            # 2 intentos ahora (dentro de ventana, pero < 5)
            f'192.168.1.100 - - [{fecha_ahora}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_ahora}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
        ]

        f.writelines(lineas)
        f.flush()

    try:
        detector = DetectorFuerzaBruta(ruta, umbral_intentos=5, ventana_segundos=600)
        eventos = await detector.procesar()

        # No debe detectar porque solo hay 2 intentos en la ventana de 10 min
        assert len(eventos) == 0, f"Se esperaba 0 eventos, se obtuvieron {len(eventos)}"
    finally:
        ruta.unlink()


@pytest.mark.asyncio
async def test_ignora_get_y_otros_metodos() -> None:
    """Pb-17: Verificar que solo detecta POST /login."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        ruta = Path(f.name)
        ahora = datetime.now(UTC)
        fecha_str = ahora.strftime("%d/%b/%Y:%H:%M:%S +0000")

        lineas = [
            f'192.168.1.100 - - [{fecha_str}] "GET /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "PUT /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "DELETE /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "POST /register HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
        ]

        f.writelines(lineas)
        f.flush()

    try:
        detector = DetectorFuerzaBruta(ruta, umbral_intentos=1)
        eventos = await detector.procesar()

        # No debe detectar porque no hay POST /login
        assert len(eventos) == 0, f"Se esperaba 0 eventos, se obtuvieron {len(eventos)}"
    finally:
        ruta.unlink()


@pytest.mark.asyncio
async def test_ignora_codigo_200_y_otros() -> None:
    """Pb-17: Verificar que solo detecta códigos 401 y 403."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        ruta = Path(f.name)
        ahora = datetime.now(UTC)
        fecha_str = ahora.strftime("%d/%b/%Y:%H:%M:%S +0000")

        lineas = [
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 200 512 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 302 0 "-" "Mozilla/5.0"\n',
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 500 256 "-" "Mozilla/5.0"\n',
        ]

        f.writelines(lineas)
        f.flush()

    try:
        detector = DetectorFuerzaBruta(ruta, umbral_intentos=1)
        eventos = await detector.procesar()

        # No debe detectar porque no hay código 401 o 403
        assert len(eventos) == 0, f"Se esperaba 0 eventos, se obtuvieron {len(eventos)}"
    finally:
        ruta.unlink()


@pytest.mark.asyncio
async def test_no_reprocesa_eventos_anteriores() -> None:
    """Pb-17: Verificar que no reprocesa eventos ya detectados."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        ruta = Path(f.name)
        ahora = datetime.now(UTC)
        fecha_str = ahora.strftime("%d/%b/%Y:%H:%M:%S +0000")

        lineas = [
            f'192.168.1.100 - - [{fecha_str}] "POST /login HTTP/1.1" 401 245 "-" "Mozilla/5.0"\n',
        ] * 5

        f.writelines(lineas)
        f.flush()

    try:
        detector = DetectorFuerzaBruta(ruta, umbral_intentos=5)

        # Primera ejecución
        eventos1 = await detector.procesar()
        assert len(eventos1) == 1

        # Segunda ejecución (mismo archivo)
        # Debe retornar 0 porque ya procesó esos eventos
        eventos2 = await detector.procesar()
        assert len(eventos2) == 0, "No debe reprocesar eventos anteriores"
    finally:
        ruta.unlink()
