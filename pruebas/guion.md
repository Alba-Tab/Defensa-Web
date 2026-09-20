# Guion mínimo de ataque y evidencia

## Alcance y precondiciones

- Ejecutar solo contra la VM de laboratorio autorizada.
- Tener nginx, Suricata, NFQUEUE y la API activos; sincronizar los relojes.
- Abrir tres vistas: `eve.json`, log de acceso nginx y API/base de incidentes.
- Anotar commit, fecha UTC, IP objetivo y versiones de Suricata/k6.

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
