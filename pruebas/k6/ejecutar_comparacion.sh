#!/usr/bin/env bash
set -euo pipefail

escenario="${1:-}"
if [[ "$escenario" != "sin-suricata" && "$escenario" != "con-suricata" ]]; then
  echo 'Uso: BASE_URL=http://IP_VM ejecutar_comparacion.sh sin-suricata|con-suricata' >&2
  exit 2
fi

if [[ -z "${BASE_URL:-}" ]]; then
  echo 'Falta BASE_URL con la URL de la VM del laboratorio.' >&2
  exit 2
fi

raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$raiz/pruebas/resultados"

ESCENARIO="$escenario" \
SUMMARY_FILE="$raiz/pruebas/resultados/k6-$escenario.json" \
k6 run "$raiz/pruebas/k6/navegacion_legitima.js"

echo "Resultado guardado en pruebas/resultados/k6-$escenario.json"
