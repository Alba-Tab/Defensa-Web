#!/usr/bin/env bash
set -euo pipefail

objetivo="${TARGET_URL:-}"
if [[ "${AUTORIZO_LAB:-NO}" != "SI" || -z "${objetivo}" ]]; then
  echo 'Uso: AUTORIZO_LAB=SI TARGET_URL=https://IP_VM bash pruebas/ataques/sqlmap.sh' >&2
  exit 2
fi

if [[ ! "${objetivo}" =~ ^https?://(localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.) ]]; then
  echo 'ERROR: TARGET_URL debe ser localhost o una IP privada del laboratorio.' >&2
  exit 2
fi

if ! command -v sqlmap >/dev/null 2>&1; then
  echo 'ERROR: sqlmap no está instalado.' >&2
  exit 127
fi

raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "${raiz}/pruebas/resultados/sqlmap"
objetivo="${objetivo%/}"

sqlmap \
  --url "${objetivo}/buscar?q=1" \
  --batch \
  --level 1 \
  --risk 1 \
  --technique B \
  --threads 1 \
  --delay 0.25 \
  --timeout 8 \
  --retries 0 \
  --flush-session \
  --output-dir "${raiz}/pruebas/resultados/sqlmap"

echo 'Revise el SID y src_ip resultantes en eve.json según pruebas/guion.md.'
