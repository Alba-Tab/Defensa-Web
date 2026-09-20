# Evidencia Pb-3 · descarte de SQLi

Fecha UTC: 2026-09-20. Entorno aislado Docker: atacante → gateway Linux con nftables/NFQUEUE y
Suricata 8.0.6 → aplicación mínima.

- Petición legítima: HTTP 200.
- SQLi de alta confianza (SID 1000001): conexión cerrada con TCP reset en 2,9 ms.
- `eve.json`: `alert.action=blocked`, IP real `172.30.10.10`, método y URI presentes.
- Log de aplicación: la petición SQLi rechazada no aparece; la legítima sí.
- Navegación legítima corta: 10/10 comprobaciones correctas con inspección y 10/10 sin ella.
- p95 sin inspección: 5,49 ms; p95 con inspección: 29,24 ms; diferencia: 23,75 ms.
- Sesión adicional de 10 minutos: 1.188 iteraciones y 2.376/2.376 comprobaciones funcionales
  correctas. El servidor mínimo devolvía 404 en `/buscar`, por lo que esa corrida no se usa para
  la comparación de `http_req_failed`; la comparación corta posterior usa HTTP 200.

Se eligió `reject` en vez de `drop`: bloquea antes de la aplicación y devuelve un TCP reset, por
lo que el cliente no espera hasta agotar su timeout. El umbral aceptable de latencia sigue siendo
una decisión del Product Owner, tal como indica la tarjeta.
