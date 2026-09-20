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
`/opt/defensa/servicio`. El informe del Sprint 1 siempre usa la plantilla local y no realiza
llamadas externas.

## Flujo HTTPS inspeccionable (Pb-29, Modo B)

```text
cliente HTTPS :443
  → nftables INPUT (baneo de Fail2ban)
  → nginx termina TLS
  → HTTP de loopback a 127.0.0.1:3000
  → nftables OUTPUT / NFQUEUE 0 con bypass
  → Suricata IPS inspecciona el contenido descifrado
  → aplicación protegida 127.0.0.1:3000
```

El puerto 80 solo responde `308` hacia HTTPS. El certificado autofirmado del laboratorio se crea
durante el aprovisionamiento en `/etc/defensa/tls`; la clave tiene modo `0600` y tanto certificados
como claves quedan excluidos de Git. Puede regenerarse de forma idempotente con:

```bash
sudo DEFENSA_TLS_IP=192.168.56.20 \
  infra/nginx/generar-certificado-lab.sh
```

nginx agrega `X-Forwarded-For` con la IP del cliente. Suricata usa el modo XFF `reverse` para
registrar esa IP como origen en EVE, aunque el socket inspeccionado sea de loopback. `suricata -T`
en `infra/verificar.sh` detecta si una versión instalada no acepta estos ajustes.

La app móvil consume la API administrativa del servicio en el puerto 8000, no el proxy de Juice
Shop en 80/443. Por eso la redirección no rompe su funcionamiento actual, pero ese canal sigue en
HTTP plano: llevarlo a HTTPS y confiar el certificado de laboratorio en Android queda como
limitación explícita fuera de Pb-29.

## Límite de tasa (Pb-15)

nginx limita por `$binary_remote_addr` después de procesar `real_ip_header`. Solo se confía en
proxies de loopback, por lo que un cliente directo no puede falsificar `X-Forwarded-For`.
El tráfico general admite 10 solicitudes por segundo y una ráfaga de 20; el login exacto de Juice
Shop (`/rest/user/login`) agrega un límite de 5 solicitudes por minuto con ráfaga de 4. Al superar
cualquiera de ellos, nginx responde 429 antes de ejecutar `proxy_pass`.

Estos límites son volumétricos y no sustituyen los baneos de Pb-6, que dependen de eventos
maliciosos correlacionados y se aplican mediante el motor de políticas y Fail2ban.
