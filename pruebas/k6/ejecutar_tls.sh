#!/usr/bin/env bash
set -euo pipefail

modo="${1:-}"
if [[ "${modo}" != "http" && "${modo}" != "https" ]]; then
  echo 'Uso: BASE_URL=https://IP_VM ejecutar_tls.sh http|https' >&2
  exit 2
fi

if [[ -z "${BASE_URL:-}" ]]; then
  echo 'Falta BASE_URL con la URL de la VM del laboratorio.' >&2
  exit 2
fi

raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "${raiz}/pruebas/resultados"

ESCENARIO="pb29-${modo}" \
TLS_INSEGURO="${TLS_INSEGURO:-NO}" \
SUMMARY_FILE="${raiz}/pruebas/resultados/k6-pb29-${modo}.json" \
k6 run "${raiz}/pruebas/k6/navegacion_legitima.js"

echo "Resultado guardado en pruebas/resultados/k6-pb29-${modo}.json"
