#!/usr/bin/env bash
set -euo pipefail

archivo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/android/app/google-services.json"
paquete='bo.uagrm.grupo13.defensa_movil'

if [[ ! -f "$archivo" ]]; then
  echo "FALTA: $archivo" >&2
  echo "Descárguelo desde la app Android registrada en Firebase (paquete: $paquete)." >&2
  exit 1
fi

if ! grep -Fq "\"package_name\": \"$paquete\"" "$archivo"; then
  echo "ERROR: google-services.json no corresponde al paquete $paquete" >&2
  exit 1
fi

if ! grep -Fq '"project_id"' "$archivo"; then
  echo 'ERROR: google-services.json no contiene project_id' >&2
  exit 1
fi

echo 'OK: configuración Android de Firebase presente y compatible.'
