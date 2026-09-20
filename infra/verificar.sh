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

comprobar_codigo_http() {
  local descripcion="$1"
  local esperado="$2"
  shift 2
  local obtenido
  obtenido="$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' "$@" || true)"
  if [[ "${obtenido}" == "${esperado}" ]]; then
    printf 'OK  %s\n' "${descripcion}"
  else
    printf 'FALLO  %s (esperado %s, obtenido %s)\n' \
      "${descripcion}" "${esperado}" "${obtenido:-sin respuesta}" >&2
    fallos=$((fallos + 1))
  fi
}

comprobar "nginx" nginx -t
comprobar "servicio nginx activo" systemctl is-active --quiet nginx
comprobar "certificado TLS vigente" openssl x509 \
  -in /etc/defensa/tls/defensa-web.crt -noout -checkend 86400
comprobar "configuración de Suricata" suricata -T \
  -c /etc/suricata/suricata.yaml -s /etc/suricata/rules/local.rules
comprobar "servicio Suricata activo" systemctl is-active --quiet suricata
comprobar "nftables" nft -c -f /etc/nftables.conf
comprobar "tabla nftables de defensa cargada" nft list table inet defensa
comprobar "servicio Fail2ban activo" systemctl is-active --quiet fail2ban
comprobar "jail Fail2ban" fail2ban-client status defensa-web
comprobar "permisos del actuador Fail2ban" sudo -u defensa sudo -n \
  /usr/bin/fail2ban-client get defensa-web banip
comprobar "servicio de defensa" systemctl is-active --quiet defensa
comprobar "API de defensa" curl -fsS http://127.0.0.1:8000/login
comprobar "aplicación protegida" curl -fsS http://127.0.0.1:3000
comprobar "salud del contenedor protegido" sh -c \
  '[ "$(docker inspect -f "{{.State.Health.Status}}" compose-app-protegida-1)" = healthy ]'
comprobar_codigo_http "redirección HTTP a HTTPS" 308 http://127.0.0.1
comprobar "proxy HTTPS" curl --noproxy '*' --cacert /etc/defensa/tls/defensa-web.crt \
  --resolve defensa-web.local:443:127.0.0.1 -fsS https://defensa-web.local

exit "${fallos}"
