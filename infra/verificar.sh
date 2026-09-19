#!/usr/bin/env bash
set -Eeuo pipefail

fallos=0
comprobar() {
  local descripcion="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    printf 'OK  %s\n' "${descripcion}"
  else
    printf 'FALLO  %s\n' "${descripcion}" >&2
    fallos=$((fallos + 1))
  fi
}

comprobar "nginx" nginx -t
comprobar "Suricata" suricata -T -c /etc/suricata/suricata.yaml -s /etc/suricata/rules/local.rules
comprobar "nftables" nft -c -f /etc/nftables.conf
comprobar "Fail2ban" fail2ban-client status defensa-web
comprobar "aplicación protegida" curl -fsS http://127.0.0.1:3000
comprobar "proxy público" curl -fsS http://127.0.0.1

exit "${fallos}"
