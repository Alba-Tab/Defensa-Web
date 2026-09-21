# Pruebas de sistema y demostración

Estas pruebas se ejecutan únicamente contra la VM o contenedor local autorizado. No apuntar a
servicios públicos ni a infraestructura de terceros.

## Contenido

- `ataques/sqli.sh`: humo controlado para comprobar detección y descarte de SQLi.
- `ataques/sqlmap.sh`: ejecución limitada de sqlmap para la aceptación de Pb-29.
- `k6/navegacion_legitima.js`: navegación normal para falsos positivos y latencia.
- `k6/limite_tasa.js`: ráfaga controlada que exige respuestas 429 para Pb-15.
- `k6/ejecutar_comparacion.sh`: conserva resultados separados con Suricata apagado/encendido.
- `k6/ejecutar_tls.sh`: conserva las mediciones HTTP/HTTPS de Pb-29.
- `guion.md`: secuencia de demostración y evidencias para Pb-2/Pb-3.

## Uso rápido

```bash
AUTORIZO_LAB=SI TARGET_URL=http://192.168.56.20 bash pruebas/ataques/sqli.sh

BASE_URL=http://192.168.56.20 \
  bash pruebas/k6/ejecutar_comparacion.sh sin-suricata
# activar Suricata/NFQUEUE en la VM
BASE_URL=http://192.168.56.20 \
  bash pruebas/k6/ejecutar_comparacion.sh con-suricata

# Pb-15: el tráfico normal no recibe 429 durante 10 minutos.
BASE_URL=http://192.168.56.20 DURACION=10m VUS=2 ESCENARIO=pb15-legitimo \
  SUMMARY_FILE=pruebas/resultados/k6-pb15-legitimo.json \
  k6 run pruebas/k6/navegacion_legitima.js

# Pb-15: una ráfaga general y otra al login sí reciben 429.
BASE_URL=http://192.168.56.20 k6 run pruebas/k6/limite_tasa.js
BASE_URL=http://192.168.56.20 RUTA=/rest/user/login METODO=POST TASA=10 \
  k6 run pruebas/k6/limite_tasa.js

# Pb-29: medir primero la línea base del Modo A, antes de habilitar la redirección.
BASE_URL=http://192.168.56.20 DURACION=10m bash pruebas/k6/ejecutar_tls.sh http

# Después del aprovisionamiento TLS, medir el Modo B con el certificado autofirmado.
BASE_URL=https://192.168.56.20 TLS_INSEGURO=SI DURACION=10m \
  bash pruebas/k6/ejecutar_tls.sh https

# Pb-29: SQLi sobre HTTPS para comprobar la alerta en eve.json.
AUTORIZO_LAB=SI CURL_INSEGURO=SI TARGET_URL=https://192.168.56.20 \
  bash pruebas/ataques/sqli.sh

# Criterio formal de Pb-29: repetir con sqlmap a baja tasa.
AUTORIZO_LAB=SI TARGET_URL=https://192.168.56.20 \
  bash pruebas/ataques/sqlmap.sh

# El límite de Pb-15 debe seguir devolviendo 429 sobre HTTPS.
BASE_URL=https://192.168.56.20 TLS_INSEGURO=SI \
  k6 run pruebas/k6/limite_tasa.js
```

Los JSON se guardan en `pruebas/resultados/`, que no debe contener secretos. La carga por defecto
es deliberadamente moderada (2 usuarios virtuales durante 30 segundos).

El límite volumétrico de Pb-15 vive en nginx y devuelve 429 antes de llegar a Juice Shop. Es
independiente del bloqueo de Pb-6: este último necesita eventos maliciosos correlacionados y crea
un baneo temporal mediante el motor de políticas y Fail2ban.

`TLS_INSEGURO=SI` y `CURL_INSEGURO=SI` solo se permiten en el laboratorio porque el certificado es
autofirmado. Para una verificación más estricta, instale `defensa-web.crt` como CA confiable y no
defina esas variables.
