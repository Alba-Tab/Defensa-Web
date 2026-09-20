# Infraestructura defensiva

La VM Ubuntu ejecuta nginx, Suricata, nftables, Fail2ban, la aplicación protegida y el
servicio de defensa. El aprovisionamiento es idempotente y no contiene secretos.

## VM reproducible

```bash
vagrant up
vagrant ssh
sudo /vagrant/infra/verificar.sh
```

Si Vagrant no está disponible, copia el repositorio a Ubuntu 24.04 y ejecuta:

```bash
sudo bash infra/provision/provision.sh
```

Antes de usar el modo real, crea `/etc/defensa/defensa.env` a partir de
`infra/systemd/defensa.env.example`, establece los secretos y despliega el servicio Python en
`/opt/defensa/backend`. El informe del Sprint 1 siempre usa la plantilla local y no realiza
llamadas externas.

## Flujo de red del MVP

```text
cliente HTTP :80
  → nftables INPUT (baneo de Fail2ban)
  → NFQUEUE 0 con bypass
  → Suricata IPS
  → nginx :80
  → aplicación protegida 127.0.0.1:3000
```

El modo HTTPS completo requiere mover la inspección al tramo HTTP descifrado entre nginx y la
aplicación. No se habilita TLS de forma ficticia en esta base.
