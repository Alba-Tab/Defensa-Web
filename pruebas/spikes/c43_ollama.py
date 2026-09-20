#!/usr/bin/env python3
import argparse
import json
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SECCIONES = ("Qué ocurrió", "Categoría OWASP", "Acción aplicada", "Recomendaciones")
MUESTRAS = (
    (
        "sqli",
        (
            "inyección SQL desde 192.0.2.50; 120 eventos en 40 segundos; "
            "la IP quedó bloqueada durante 10 minutos; OWASP A03:2021"
        ),
    ),
    (
        "xss",
        (
            "XSS reflejado desde 198.51.100.22; 8 eventos; las peticiones fueron descartadas; "
            "OWASP A03:2021"
        ),
    ),
    (
        "traversal",
        (
            "path traversal desde 203.0.113.9; recurso sensible solicitado; se generó una alerta "
            "sin bloqueo; OWASP A01:2021"
        ),
    ),
)


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Spike C-43: latencia de fichas con Ollama"
    )
    parser.add_argument("--url", default="http://127.0.0.1:11434")
    parser.add_argument("--modelo", default="llama3.2:1b")
    parser.add_argument("--limite", type=float, default=20.0)
    parser.add_argument("--salida", type=Path)
    return parser.parse_args()


def generar(
    url: str, modelo: str, hechos: str, limite: float
) -> tuple[dict[str, Any], float]:
    prompt = (
        "Redacta una ficha defensiva breve en español usando solo los hechos dados. "
        "Escribe exactamente estos cuatro encabezados, respetando mayúsculas y acentos: "
        f"{', '.join(SECCIONES)}. No agregues otros encabezados. Hechos: {hechos}."
    )
    cuerpo = json.dumps(
        {
            "model": modelo,
            "system": (
                "Eres un analista de ciberseguridad defensiva. Resumes incidentes ya detectados "
                "para que un administrador pueda responder. No das instrucciones de ataque."
            ),
            "prompt": prompt,
            "stream": False,
            "keep_alive": "5m",
            "options": {"temperature": 0, "num_predict": 220},
        }
    ).encode()
    solicitud = urllib.request.Request(
        f"{url.rstrip('/')}/api/generate",
        data=cuerpo,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    inicio = time.perf_counter()
    with urllib.request.urlopen(solicitud, timeout=limite + 5) as respuesta:
        datos = json.load(respuesta)
    return datos, time.perf_counter() - inicio


def main() -> int:
    args = argumentos()
    mediciones: list[dict[str, Any]] = []
    for nombre, hechos in MUESTRAS:
        respuesta, segundos = generar(args.url, args.modelo, hechos, args.limite)
        texto = str(respuesta.get("response", ""))
        secciones_faltantes = [seccion for seccion in SECCIONES if seccion not in texto]
        mediciones.append(
            {
                "muestra": nombre,
                "segundos": round(segundos, 3),
                "carga_modelo_segundos": round(
                    respuesta.get("load_duration", 0) / 1e9, 3
                ),
                "tokens_generados": respuesta.get("eval_count", 0),
                "secciones_faltantes": secciones_faltantes,
                "cumple": segundos < args.limite and not secciones_faltantes,
            }
        )

    informe = {
        "spike": "C-43",
        "fecha_utc": datetime.now(UTC).isoformat(),
        "url": args.url,
        "modelo": args.modelo,
        "limite_segundos": args.limite,
        "mediciones": mediciones,
        "maximo_segundos": max(medicion["segundos"] for medicion in mediciones),
        "cumple": all(medicion["cumple"] for medicion in mediciones),
    }
    serializado = json.dumps(informe, ensure_ascii=False, indent=2)
    print(serializado)
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(serializado + "\n", encoding="utf-8")
    return 0 if informe["cumple"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
