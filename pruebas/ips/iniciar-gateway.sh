#!/usr/bin/env bash
set -Eeuo pipefail

nft -f /opt/pruebas/cola.nft
suricata -q 0 \
  -c /etc/suricata/suricata.yaml \
  -S /opt/pruebas/local.rules \
  -l /var/log/suricata &
echo "$!" >/run/suricata-prueba.pid

terminar() {
  if [[ -f /run/suricata-prueba.pid ]]; then
    kill "$(cat /run/suricata-prueba.pid)" 2>/dev/null || true
  fi
}
trap terminar EXIT TERM INT
while true; do
  sleep 3600 &
  wait "$!"
done
