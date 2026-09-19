#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Este script debe ejecutarse como root." >&2
  exit 1
fi

REPO_DIR="${REPO_DIR:-/vagrant}"
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates curl docker.io docker-compose-v2 fail2ban nftables nginx \
  python3 python3-venv rsync sudo suricata suricata-update acl

install -d -m 0755 /etc/defensa /var/log/defensa /opt/defensa
touch /var/log/defensa/acciones.log

install -m 0644 "${REPO_DIR}/infra/nginx/defensa-web.conf" /etc/nginx/sites-available/defensa-web
ln -sfn /etc/nginx/sites-available/defensa-web /etc/nginx/sites-enabled/defensa-web
rm -f /etc/nginx/sites-enabled/default

install -m 0644 "${REPO_DIR}/infra/suricata/local.rules" /etc/suricata/rules/local.rules
install -m 0644 "${REPO_DIR}/infra/suricata/disable.conf" /etc/suricata/disable.conf
install -m 0644 "${REPO_DIR}/infra/suricata/enable.conf" /etc/suricata/enable.conf
install -m 0644 "${REPO_DIR}/infra/logrotate/suricata-eve" /etc/logrotate.d/suricata-eve
install -d -m 0755 /etc/systemd/system/suricata.service.d
install -m 0644 "${REPO_DIR}/infra/systemd/suricata-nfq.conf" \
  /etc/systemd/system/suricata.service.d/nfq.conf

install -m 0644 "${REPO_DIR}/infra/fail2ban/jail.local" /etc/fail2ban/jail.d/defensa-web.local
install -m 0644 "${REPO_DIR}/infra/fail2ban/defensa-web.conf" /etc/fail2ban/filter.d/defensa-web.conf
install -m 0755 "${REPO_DIR}/infra/nftables/defensa.nft" /etc/nftables.conf

if ! id defensa >/dev/null 2>&1; then
  adduser --system --group --home /opt/defensa --shell /usr/sbin/nologin defensa
fi
setfacl -R -m u:defensa:rX /var/log/suricata
setfacl -d -m u:defensa:rX /var/log/suricata
install -m 0440 "${REPO_DIR}/infra/sudoers/defensa" /etc/sudoers.d/defensa

install -m 0644 "${REPO_DIR}/infra/systemd/defensa.service" /etc/systemd/system/defensa.service
if [[ ! -f /etc/defensa/defensa.env ]]; then
  install -m 0640 -o root -g defensa \
    "${REPO_DIR}/infra/systemd/defensa.env.example" /etc/defensa/defensa.env
fi

rsync -a --delete \
  --exclude '.pytest_cache' --exclude '__pycache__' --exclude '*.egg-info' \
  "${REPO_DIR}/servicio/" /opt/defensa/servicio/
python3 -m venv /opt/defensa/venv
/opt/defensa/venv/bin/python -m pip install --upgrade pip
/opt/defensa/venv/bin/python -m pip install '/opt/defensa/servicio[real]'
install -d -m 0750 -o defensa -g defensa /opt/defensa/datos /opt/defensa/modelos
chown -R defensa:defensa /opt/defensa/servicio

suricata-update --disable-conf /etc/suricata/disable.conf \
  --enable-conf /etc/suricata/enable.conf || true
nft -c -f /etc/nftables.conf
nginx -t
suricata -T -c /etc/suricata/suricata.yaml -s /etc/suricata/rules/local.rules

systemctl daemon-reload
systemctl enable --now docker nginx
systemctl enable --now nftables
systemctl enable --now fail2ban
systemctl enable --now suricata
systemctl enable defensa
docker compose -f "${REPO_DIR}/infra/compose/app-protegida.yaml" up -d

echo "Aprovisionamiento terminado. Ejecuta: sudo ${REPO_DIR}/infra/verificar.sh"
