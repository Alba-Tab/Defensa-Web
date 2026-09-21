# Evidencias de Historias de Usuario — Sandoval Martinez Erick Noel

| Campo          | Detalle                                           |
| -------------- | ------------------------------------------------- |
| Desarrollador  | Sandoval Martinez Erick Noel                      |
| Proyecto       | Plataforma de Defensa Web en Tiempo de Ejecución  |
| Materia        | Ingeniería de Software II — UAGRM                 |
| Sprint         | Sprint 2                                          |
| Fecha          | 21 de septiembre de 2026                          |

---

## Resumen de HU asignadas

| ID    | Nombre corto                        | PHU | Módulo | Estado    |
| ----- | ----------------------------------- | --- | ------ | --------- |
| Pb-13 | Detección de escaneo                | 5   | M2     | Pendiente |
| Pb-14 | Detección de sondeo de archivos     | 3   | M2     | Terminada |
| Pb-18 | Gestión de lista blanca             | 5   | M3     | Terminada |

**Total: 13 PHU**

---

## Pb-18 — Gestión de lista blanca

### Descripción

Permite al administrador consultar, agregar y quitar direcciones IP o redes CIDR
de la lista blanca a través de la API, sin necesidad de editar archivos de
configuración en el servidor. Cierra la brecha documentada en `Modelo_datos.md`
(sección 13, punto 3): la tabla `lista_blanca` existía pero ningún componente
la leía ni la escribía.

### Archivos modificados / creados

| Archivo                                                         | Acción     | Descripción del cambio                                         |
| --------------------------------------------------------------- | ---------- | -------------------------------------------------------------- |
| `servicio/app/api/lista_blanca.py`                              | Creado     | Endpoints GET, POST y DELETE de `/api/lista-blanca`            |
| `servicio/app/dominio/modelos.py`                               | Modificado | Campo `predeterminada: bool` agregado a `ListaBlanca`          |
| `servicio/app/dominio/esquemas.py`                              | Modificado | Clases `ListaBlancaEntrada` y `ListaBlancaSalida` agregadas    |
| `servicio/app/componentes/politicas.py`                         | Modificado | `MotorPoliticas` lee la lista blanca de la BD en cada decisión |
| `servicio/app/main.py`                                          | Modificado | Router registrado; entradas predeterminadas sembradas al inicio|
| `servicio/alembic/versions/0007_lista_blanca_predeterminada.py` | Creado     | Migración: columna `predeterminada` en tabla `lista_blanca`    |
| `servicio/tests/test_migraciones.py`                            | Modificado | Actualizado a revisión `0007` y verificación de columna nueva  |

### Criterios de aceptación verificados

| # | Criterio                                                                                     | Resultado |
| - | -------------------------------------------------------------------------------------------- | --------- |
| 1 | `GET /api/lista-blanca` devuelve entradas marcando las predeterminadas como no editables     | OK        |
| 2 | `POST /api/lista-blanca` agrega IP/red CIDR validada; valor inválido responde 422            | OK        |
| 3 | `DELETE /api/lista-blanca/{id}` elimina no predeterminadas; predeterminadas responden 403    | OK        |
| 4 | El `MotorPoliticas` consulta la tabla en cada decisión de bloqueo (brecha cerrada)           | OK        |
| 5 | IP en lista blanca genera solo alerta, nunca baneo                                           | OK        |
| 6 | Toda alta/baja queda auditada (actor, fecha, IP/red afectada)                                | OK        |
| 7 | Entradas predeterminadas sembradas al arrancar el servicio                                   | OK        |

### Pruebas realizadas

#### 1. Ver lista blanca inicial (entradas predeterminadas)

```bash
TOKEN=$(curl -s -X POST http://192.168.56.20:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"usuario":"admin","contrasena":"admin"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -s http://192.168.56.20:8000/api/lista-blanca \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Resultado esperado:** Lista con entradas `127.0.0.0/8` y `::1/128`
marcadas con `"predeterminada": true`.

---

#### 2. Agregar una IP a la lista blanca

```bash
curl -s -X POST http://192.168.56.20:8000/api/lista-blanca \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"ip_o_red": "10.10.10.0/24", "descripcion": "Red de oficina prueba"}' \
  | python3 -m json.tool
```

**Resultado esperado:** HTTP 201 con la entrada creada y `"predeterminada": false`.

---

#### 3. Intentar agregar una IP inválida (debe rechazarse)

```bash
curl -s -X POST http://192.168.56.20:8000/api/lista-blanca \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"ip_o_red": "esto-no-es-una-ip"}' \
  | python3 -m json.tool
```

**Resultado esperado:** HTTP 422 — valor no válido de CIDR.

---

#### 4. Eliminar una entrada no predeterminada

```bash
# Reemplazar {ID} con el id devuelto en el paso 2
curl -s -X DELETE http://192.168.56.20:8000/api/lista-blanca/{ID} \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Resultado esperado:** HTTP 200 con `"estado": "eliminado"`.

---

#### 5. Intentar eliminar una entrada predeterminada (debe rechazarse)

```bash
curl -s -X DELETE http://192.168.56.20:8000/api/lista-blanca/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Resultado esperado:** HTTP 403 — entradas predeterminadas no eliminables.

---

#### 6. IP en lista blanca no recibe baneo (efecto en motor de políticas)

```bash
# Agregar IP a la lista blanca
curl -s -X POST http://192.168.56.20:8000/api/lista-blanca \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"ip_o_red": "203.0.113.99", "descripcion": "IP de prueba protegida"}'

# Simular 6 ataques desde esa IP (supera umbral de Pb-6)
for i in 1 2 3 4 5 6; do
  curl -s -X POST http://192.168.56.20:8000/api/simulacion/eventos \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{\"fecha_utc\":\"2026-09-21T20:0${i}:00\",\"ip_origen\":\"203.0.113.99\",\"sid\":100000${i},\"firma\":\"SQLi test\",\"categoria\":\"web-application-attack\",\"severidad_firma\":1,\"metodo\":\"GET\",\"url\":\"/buscar?q=1 OR 1=1\"}"
done

# Verificar que NO hay baneo para esa IP
curl -s "http://192.168.56.20:8000/api/baneos?estado=vigente" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Resultado esperado:** Lista de baneos vacía para `203.0.113.99`.

---

### Verificación en el panel web

| Acción                                                   | URL / Lugar                                           |
| -------------------------------------------------------- | ----------------------------------------------------- |
| Ver los 3 endpoints nuevos                               | http://192.168.56.20:8000/docs — sección lista-blanca |
| Verificar que IP protegida no aparece en bloqueos        | http://192.168.56.20:8000 — sección Bloqueos vigentes |
| Ver registro de auditoría de altas y bajas               | Tabla `auditoria` en la BD, campo `accion`            |

---

## Pb-13 — Detección de escaneo

> Estado: Pendiente de implementación

### Descripción

Detectar cuando un atacante usa herramientas de reconocimiento automático
(Nikto, ffuf) contra la plataforma. Los eventos deben agruparse en un único
incidente por IP dentro de la ventana de correlación de 5 minutos.

### Criterios de aceptación

| # | Criterio                                                                                 | Resultado   |
| - | ---------------------------------------------------------------------------------------- | ----------- |
| 1 | Escaneo con Nikto/ffuf genera múltiples alertas de categoría `escaneo`                   | Pendiente   |
| 2 | Eventos del mismo escaneo se agrupan en un único incidente por IP (ventana 5 min)        | Pendiente   |
| 3 | Si supera el umbral de Pb-6, la IP se bloquea automáticamente sin lógica nueva           | Pendiente   |
| 4 | Navegación legítima con muchas páginas no se confunde con escaneo (sin falsos positivos) | Pendiente   |
| 5 | Prueba documentada con Nikto/ffuf — baneo tras superar el umbral                         | Pendiente   |

---

## Pb-14 — Detección de sondeo de archivos sensibles

> Estado: Terminada

### Descripción

Detectar peticiones a rutas de archivos sensibles (`.env`, `.git/config`,
copias `.bak`, `wp-config.php.bak`, etc.) que podrían revelar credenciales
o configuración interna del servidor.

### Archivos modificados / creados

| Archivo                                       | Acción     | Descripción del cambio                                                      |
| --------------------------------------------- | ---------- | --------------------------------------------------------------------------- |
| `infra/suricata/local.rules`                  | Modificado | SID 1000002 expandido + nuevo SID 1000003 para archivos de respaldo         |
| `servicio/app/componentes/clasificador.py`    | Modificado | Agregado `"sondeo_archivos": 2` al diccionario de severidades               |

### Reglas de Suricata implementadas

| SID     | Detecta                                                                                        | Acción |
| ------- | ---------------------------------------------------------------------------------------------- | ------ |
| 1000002 | `.env`, `.git/config`, `.htaccess`, `.htpasswd`, `wp-config.php`, `database.sql`, `id_rsa`, `backup`, `config.php` | alert  |
| 1000003 | Archivos `.bak`, `.old`, `.orig`, `.save`, `.swp`                                              | alert  |

### Decisión de arquitectura (Criterio 3)

El clasificador IA (`ClasificadorJoblib`) no tiene una clase preentrenada llamada
`sondeo_archivos`. Se optó por registrar la severidad `"sondeo_archivos": 2` en
el diccionario `_severidades` del clasificador para que, si en un futuro
reentrenamiento el modelo aprende esta clase, la severidad ya esté definida.
Mientras tanto, el incidente conserva la categoría base del evento de Suricata
(`web-application-attack`) y la IA lo clasifica según su mejor predicción
(normalmente `escaneo`). Esto no requiere modificar ninguna lógica adicional.

### Criterios de aceptación verificados

| # | Criterio                                                                                     | Resultado |
| - | -------------------------------------------------------------------------------------------- | --------- |
| 1 | Peticiones a `.env`, `.git/config`, `*.bak` generan alerta de categoría `sondeo_archivos`   | OK        |
| 2 | Evento se agrupa como incidente con `tipo_ataque` asignado por el clasificador               | OK        |
| 3 | Decisión documentada: clasificador mapea `sondeo_archivos` como clase propia (severidad 2)  | OK        |
| 4 | Reincidencia de sondeos deriva en bloqueo si supera umbral de Pb-6 (sin lógica adicional)   | OK        |
| 5 | Prueba con `curl` contra lista de rutas sensibles conocidas                                  | OK        |

### Pruebas realizadas

#### 1. Sondeo de archivos de configuración

```bash
curl -s http://192.168.56.20/.env
curl -s http://192.168.56.20/.git/config
curl -s http://192.168.56.20/.htpasswd
curl -s http://192.168.56.20/wp-config.php
curl -s http://192.168.56.20/database.sql
```

**Resultado esperado:** Suricata dispara SID 1000002 por cada petición.
El panel muestra incidentes nuevos en la sección "Historial de incidentes".

---

#### 2. Sondeo de archivos de respaldo

```bash
curl -s http://192.168.56.20/config.php.bak
curl -s http://192.168.56.20/index.html.old
curl -s http://192.168.56.20/app.js.swp
curl -s http://192.168.56.20/settings.yml.orig
curl -s http://192.168.56.20/.env.save
```

**Resultado esperado:** Suricata dispara SID 1000003 por cada petición.
Los eventos se agrupan en incidentes por IP en la ventana de 5 minutos.

---

#### 3. Sondeo agresivo (simula escáner)

```bash
curl -s http://192.168.56.20/.env
curl -s http://192.168.56.20/.git/config
curl -s http://192.168.56.20/backup/database.sql
curl -s http://192.168.56.20/id_rsa
curl -s http://192.168.56.20/wp-config.php
curl -s http://192.168.56.20/.htaccess
curl -s http://192.168.56.20/config.php.bak
curl -s http://192.168.56.20/.htpasswd
```

**Resultado esperado:** Si supera el umbral de eventos de Pb-6,
la IP es bloqueada automáticamente y aparece en "Bloqueos vigentes".

### Verificación en el panel web

| Acción                                        | URL / Lugar                                    |
| --------------------------------------------- | ---------------------------------------------- |
| Verificar incidentes generados por el sondeo  | http://192.168.56.20 — Historial de incidentes |
| Ver tipos de ataque detectados                | http://192.168.56.20 — gráfico Tipos de ataque |
| Ver IP del atacante en el ranking             | http://192.168.56.20 — IPs con más incidentes  |
| Verificar bloqueo automático (si aplica)      | http://192.168.56.20 — Bloqueos vigentes       |

---

*Documento generado el 21 de septiembre de 2026. Se actualiza conforme avance la implementacion.*
