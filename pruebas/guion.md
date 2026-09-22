# Guion mínimo de ataque y evidencia

## Alcance y precondiciones

- Ejecutar solo contra la VM de laboratorio autorizada.
- Tener nginx, Suricata, NFQUEUE y la API activos; sincronizar los relojes.
- Abrir tres vistas: `eve.json`, log de acceso nginx y API/base de incidentes.
- Anotar commit, fecha UTC, IP objetivo y versiones de Suricata/k6.

## Pb-11: detectar inyección XSS

1. Levantar la VM con `vagrant up` y asegurar que Suricata está corriendo:
   ```bash
   vagrant ssh
   sudo systemctl status suricata
   ```

2. Ejecutar ataque XSS con script tag:
   ```bash
   curl "http://192.168.56.20:3000/search?q=%3Cscript%3Ealert(1)%3C/script%3E"
   ```

3. Verificar que Suricata detectó el ataque:
   ```bash
   sudo tail -f /var/log/suricata/eve.json | jq 'select(.alert.signature_id == 1000005)'
   ```

4. Guardar la línea de `eve.json` que incluya: fecha, IP, SID=1000005, firma="DEFENSA XSS detectado", categoría="Web Application Attack".

5. Verificar que el servicio creó un `Incidente` con `tipo_ataque = "xss"`:
   ```bash
   # En otra terminal, con token de admin:
   curl -H "Authorization: Bearer $TOKEN" http://192.168.56.20:8000/api/incidentes | jq '.[] | select(.tipo_ataque == "xss")'
   ```

6. Evidencia: captura de eve.json con SID 1000005 y captura del incidente en API con tipo_ataque="xss".

**Payloads probados**:
- `<script>alert(1)</script>` → SID 1000005
- `onclick=alert(1)` → SID 1000006
- POST con `<img src=x onerror=alert(1)>` → SID 1000007

## Pb-12: detectar path traversal

1. Levantar la VM con `vagrant up` y asegurar que Suricata está corriendo:
   ```bash
   vagrant ssh
   sudo systemctl status suricata
   ```

2. Ejecutar ataque path traversal (codificado):
   ```bash
   curl "http://192.168.56.20:3000/download?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd"
   ```

3. Verificar que Suricata detectó el ataque (cualquiera de los SID 1000008-1000010):
   ```bash
   sudo tail -f /var/log/suricata/eve.json | jq 'select(.alert.signature_id >= 1000008 and .alert.signature_id <= 1000010)'
   ```

4. Guardar la línea de `eve.json` que incluya: fecha, IP, SID=1000008/1000009/1000010, firma="DEFENSA path traversal", categoría="Web Application Attack".

5. Verificar que el servicio creó un `Incidente` con `tipo_ataque = "traversal"`:
   ```bash
   # En otra terminal, con token de admin:
   curl -H "Authorization: Bearer $TOKEN" http://192.168.56.20:8000/api/incidentes | jq '.[] | select(.tipo_ataque == "traversal")'
   ```

6. Evidencia: captura de eve.json con SID 1000008/1000009/1000010 y captura del incidente en API con tipo_ataque="traversal".

**Payloads probados**:
- `../../../../etc/passwd` → SID 1000008 (patrón básico)
- `..%2F..%2Fetc%2Fpasswd` → SID 1000009 (codificado)
- `/var/log` o `/etc/shadow` → SID 1000010 (rutas sensibles)

**Limitaciones conocidas**:
- Doble codificación (`%252e%252e%252f` = `%2e%2e%2f` decodificado dos veces) puede evadir las reglas
- Paths Windows (`..\..\config`) no se detectan (fuera de alcance MVP)

## Pb-2: detectar inyección SQL

1. Dejar Suricata en IDS o IPS y vaciar solo las vistas de terminal, no los logs.
2. Ejecutar:

   ```bash
   AUTORIZO_LAB=SI TARGET_URL=http://<IP_VM> bash pruebas/ataques/sqli.sh
   ```

3. Guardar la línea de `eve.json` que incluya fecha, IP, SID, firma, categoría y URL.
4. Verificar que el servicio creó un `Evento` y lo vinculó a un `Incidente`.
5. Evidencia: captura/archivo de los dos registros y hora coincidente.

## Pb-3: descartar y no producir falsos positivos

1. Con la regla `reject` activa, repetir el ataque. La conexión debe cerrarse de inmediato y la
   petición maliciosa no debe llegar al access log de nginx. Se eligió `reject` en lugar de `drop`:
   ambas acciones bloquean, pero `reject` devuelve un TCP reset y evita que el cliente espere hasta
   agotar su timeout.
2. Ejecutar navegación legítima durante 30 s (o 10 min para aceptación final):

   ```bash
   BASE_URL=http://<IP_VM> DURACION=10m \
     bash pruebas/k6/ejecutar_comparacion.sh con-suricata
   ```

3. Confirmar cero alertas `reject` y cero baneos para el origen legítimo.
4. Desactivar temporalmente la inspección únicamente en la VM aislada y medir la línea base:

   ```bash
   BASE_URL=http://<IP_VM> DURACION=10m \
     bash pruebas/k6/ejecutar_comparacion.sh sin-suricata
   ```

5. Comparar `http_req_duration` p(95) en ambos JSON y calcular:
   `latencia_agregada_ms = p95_con_suricata - p95_sin_suricata`.

## Registro de resultado

| Campo | Valor |
|---|---|
| Commit | |
| Fecha UTC | |
| Regla/SID | |
| SQLi aparece en eve.json | sí / no |
| SQLi ausente de access.log | sí / no |
| Bloqueos falsos positivos | |
| p95 sin Suricata (ms) | |
| p95 con Suricata (ms) | |
| Latencia agregada (ms) | |
| Observaciones | |

La prueba falla si falta un campo estructurado del evento, si la petición maliciosa llega a nginx
con la regla de descarte activa o si una petición legítima es descartada/baneada.

## Pb-29: repetir la detección detrás de HTTPS

1. Ejecutar `sudo /vagrant/infra/verificar.sh` y confirmar que pasan el certificado, la
   redirección, nginx, Suricata y nftables.
2. Enviar sqlmap a baja tasa por el punto de entrada TLS:

   ```bash
   AUTORIZO_LAB=SI TARGET_URL=https://192.168.56.20 \
     bash pruebas/ataques/sqlmap.sh
   ```

3. Ejecutar el mismo lanzador contra la línea base HTTP de Modo A si esa evidencia aún no existe.
   Confirmar en `eve.json` el mismo SID/firma de SQLi en ambos modos y verificar que `src_ip`
   corresponde al cliente, no a `127.0.0.1`.
4. Ejecutar las ráfagas de Pb-15 con `BASE_URL=https://192.168.56.20 TLS_INSEGURO=SI` y comprobar
   respuestas 429 sin errores 5xx.
5. Comparar el p(95) de `k6-pb29-http.json` y `k6-pb29-https.json`. La línea base HTTP debe haberse
   obtenido antes de habilitar la redirección 308.

La prueba falla si nginx no presenta el certificado, si HTTP no redirige, si EVE pierde la IP
original, si SQLi deja de generar alerta o si el límite de tasa no opera sobre HTTPS.
