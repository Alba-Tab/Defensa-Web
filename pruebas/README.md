# Pruebas de sistema y demostración

Estas pruebas se ejecutan únicamente contra la VM o contenedor local autorizado. No apuntar a
servicios públicos ni a infraestructura de terceros.

## Contenido

- `ataques/sqli.sh`: humo controlado para comprobar detección y descarte de SQLi.
- `k6/navegacion_legitima.js`: navegación normal para falsos positivos y latencia.
- `k6/ejecutar_comparacion.sh`: conserva resultados separados con Suricata apagado/encendido.
- `guion.md`: secuencia de demostración y evidencias para Pb-2/Pb-3.

## Uso rápido

```bash
AUTORIZO_LAB=SI TARGET_URL=http://192.168.56.10 bash pruebas/ataques/sqli.sh

BASE_URL=http://192.168.56.10 \
  bash pruebas/k6/ejecutar_comparacion.sh sin-suricata
# activar Suricata/NFQUEUE en la VM
BASE_URL=http://192.168.56.10 \
  bash pruebas/k6/ejecutar_comparacion.sh con-suricata
```

Los JSON se guardan en `pruebas/resultados/`, que no debe contener secretos. La carga por defecto
es deliberadamente moderada (2 usuarios virtuales durante 30 segundos).
