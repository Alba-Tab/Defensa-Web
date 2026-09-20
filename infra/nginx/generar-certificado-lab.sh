#!/usr/bin/env bash
set -Eeuo pipefail

directorio="${DEFENSA_TLS_DIR:-/etc/defensa/tls}"
ip_laboratorio="${DEFENSA_TLS_IP:-192.168.56.20}"
nombre_dns="${DEFENSA_TLS_DNS:-defensa-web.local}"
certificado="${directorio}/defensa-web.crt"
clave="${directorio}/defensa-web.key"

if [[ "${EUID}" -ne 0 && "${DEFENSA_TLS_PERMITIR_USUARIO:-NO}" != "SI" ]]; then
  echo "Este script debe ejecutarse como root." >&2
  exit 1
fi

install -d -m 0700 "${directorio}"
if [[ ! -s "${certificado}" || ! -s "${clave}" ]]; then
  umask 077
  openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 825 \
    -subj "/CN=${nombre_dns}" \
    -addext "subjectAltName=DNS:${nombre_dns},IP:${ip_laboratorio},IP:127.0.0.1" \
    -keyout "${clave}" \
    -out "${certificado}"
fi

chmod 0600 "${clave}"
chmod 0644 "${certificado}"
openssl x509 -in "${certificado}" -noout -checkend 86400 >/dev/null
echo "Certificado de laboratorio listo en ${certificado}"
