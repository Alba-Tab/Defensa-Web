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

1. Con la regla `drop` activa, repetir el ataque. La respuesta debe bloquearse o vencer por timeout,
   según la acción elegida. Confirmar que la petición maliciosa no llegó al access log de nginx.
2. Ejecutar navegación legítima durante 30 s (o 10 min para aceptación final):

   ```bash
   BASE_URL=http://<IP_VM> DURACION=10m \
     bash pruebas/k6/ejecutar_comparacion.sh con-suricata
   ```

3. Confirmar cero alertas `drop` y cero baneos para el origen legítimo.
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
