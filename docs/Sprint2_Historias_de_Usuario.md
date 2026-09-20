# Plataforma de Defensa Web en Tiempo de Ejecución
## Sprint 2: historias de usuario (cierre del Product Backlog)

| Campo | Detalle |
|---|---|
| Proyecto | Plataforma de Defensa Web en Tiempo de Ejecución |
| Materia | Ingeniería de Software II, UAGRM |
| Grupo | 13 |
| Proceso | Scrum |
| Duración del sprint | 2 semanas (confirmado con el docente) |
| Versión | 1.1 (PHU estimados y desarrolladores asignados) |
| Fecha | 20 de septiembre de 2026 |

> **Estado del documento.** Los Puntos de Historia de Usuario (PHU) se estimaron con Planning Poker sobre la escala de Fibonacci (1, 2, 3, 5, 8): **77 PHU en total**. La numeración de las HU es la del Product Backlog (`docs/sprint 0.md`, sección de Historias) y no cambia. Este documento cubre **las 16 historias que quedaron fuera del Sprint 1** (`docs/Sprint1_Cimientos_y_Tarjetas_HU.md`): con ellas se completan las **29 historias** del Product Backlog. Pb-15 y Pb-29 ya están **Terminadas** (commits `6f05d87` y `49f3cfb`).

---

## 1. Alcance: las 16 historias restantes

El Sprint 1 implementó 13 de las 29 HU (Pb-1 a Pb-10, Pb-20, Pb-27, Pb-28). El Sprint 2 implementa **todas las que faltan**, sin dejar HU pendiente para un sprint 3:

| Módulo | HU de este sprint | Motivo (qué queda fuera en Sprint 1) |
|---|---|---|
| M1. Enrutamiento | Pb-15, Pb-29 | Límite de tasa y terminación TLS, según `docs/sprint 0.md`: "Este sprint no incluye HU de M1" |
| M2. Inspección y bloqueo | Pb-11, Pb-12, Pb-13, Pb-14 | Aditivas sobre la misma tubería de Pb-2/Pb-3: XSS, path traversal, escaneo y sondeo de archivos |
| M3. Respuesta por dirección | Pb-16, Pb-17, Pb-18 | Refinan el bloqueo de Pb-6: duración progresiva, fuerza bruta y gestión de lista blanca |
| M4. Correlación y persistencia | Pb-21 | Filtros de historial sobre `GET /api/incidentes` |
| M5. IA local | Pb-19 | Mejora de Pb-7 con Ollama; no era condición para el requisito técnico 1 (ya cumplido por Pb-20 en el Sprint 1) |
| M6. Panel web | Pb-22, Pb-23, Pb-24, Pb-25, Pb-26 | El móvil fue el único canal del MVP del Sprint 1 |

### Cimientos que continúan del Sprint 1

Tres tareas habilitadoras ya definidas en `Sprint1_Cimientos_y_Tarjetas_HU.md` no bloquearon el Sprint 1 porque son la base de este sprint. Se retoman aquí, no se redefinen:

- **C-32** — Ollama instalado en el equipo anfitrión (habilita Pb-19).
- **C-33** — Esqueleto del panel (Jinja2, HTMX, Alpine.js, Chart.js, sin CDN) (habilita Pb-22 a Pb-26).
- **C-43** (spike 5) — La ficha con IA se genera en menos de 20 s en la máquina de la demostración, o se decide un modelo más pequeño (condición de éxito de Pb-19).

Además, dos brechas de implementación quedaron documentadas y **este sprint las cierra** porque coinciden con sus propias HU:

- `Modelo_datos.md` (decisión abierta 1): Fail2ban banea por fuerza bruta leyendo `access.log`, sin pasar por Suricata, y el servicio no se entera del baneo para crear el incidente. Lo resuelve **Pb-17**.
- `Modelo_datos.md` (sección 13, punto 1): la escala de `incidente.severidad` hoy no invierte la de la firma y no llega a `4 (crítica)`. Lo resuelve **Pb-16**, que introduce la reincidencia.
- `Modelo_datos.md` (sección 13, punto 3): la tabla `lista_blanca` existe pero ningún componente la lee ni la escribe; la exclusión real usa una variable de entorno. Lo resuelve **Pb-18**.
- `Modelo_datos.md` (sección 13, punto 7): `GET /api/eventos` (SSE) figuraba como no implementado, aunque ya existía una primera versión. **Pb-24 cerró la brecha**: el navegador consume el canal con cookie `HttpOnly`, el servidor emite identificadores, repone desde SQLite los incidentes posteriores a `Last-Event-ID` y corta la transmisión al vencer la sesión.

---

## 2. Historias de usuario del Sprint 2

Orden lógico de funcionamiento: cada HU depende solo de las anteriores de esta lista o de HU ya cerradas en el Sprint 1.

| Orden | ID | Nombre corto de HU | Prioridad | Módulo | Depende de | PHU | Desarrollador | Estado |
|---|---|---|---|---|---|---|---|---|
| 1 | Pb-15 | Límite de tasa | Media | M1 | Cimientos (nginx, Sprint 1) | **3** | Vargas Figueroa Jairo Moises | Terminada |
| 2 | Pb-29 | Terminación TLS | Media | M1 | Pb-15 | **5** | Vargas Figueroa Jairo Moises | Terminada |
| 3 | Pb-11 | Detección de XSS | Media | M2 | Pb-2, Pb-3 | **5** | Aldana Claure Brayan | Pendiente |
| 4 | Pb-12 | Detección de path traversal | Media | M2 | Pb-2, Pb-3 | **3** | Aldana Claure Brayan | Pendiente |
| 5 | Pb-13 | Detección de escaneo | Media | M2 | Pb-2, Pb-3, Pb-6 | **5** | Sandoval Martinez Erick | Pendiente |
| 6 | Pb-14 | Detección de sondeo de archivos | Media | M2 | Pb-2, Pb-3 | **3** | Sandoval Martinez Erick | Pendiente |
| 7 | Pb-16 | Bloqueo progresivo | Media | M3 | Pb-6 | **5** | Soldado Capuma Brandon | Pendiente |
| 8 | Pb-17 | Bloqueo por fuerza bruta | Media | M3 | Pb-1, Pb-6 | **8** | Soldado Capuma Brandon | Pendiente |
| 9 | Pb-18 | Gestión de lista blanca | Media | M3 | Pb-6 | **5** | Sandoval Martinez Erick | Pendiente |
| 10 | Pb-19 | Informe con IA local | Media | M5 | Pb-7; C-32; spike 5 (C-43) | **8** | Vargas Figueroa Jairo Moises | Aplazada por decisión del equipo |
| 11 | Pb-21 | Historial consultable | Media | M4 | Pb-5 | **3** | Aldana Claure Brayan | Terminada |
| 12 | Pb-22 | Detalle de incidente (panel) | Media | M6 | Pb-5, Pb-7, Pb-21; C-33 | **8** | Garcia Taboada Brayan Albaro | Terminada |
| 13 | Pb-25 | Estado de componentes (panel) | Media | M6 | Pb-4; C-33 | **5** | Garcia Taboada Brayan Albaro | Implementada; verificación VM pendiente |
| 14 | Pb-24 | Alertas en tiempo real (panel) | Media | M6 | Pb-5, Pb-22 | **3** | Vargas Figueroa Jairo Moises | Terminada |
| 15 | Pb-26 | Tablero de métricas (panel) | Media | M6 | Pb-5, Pb-6, Pb-20 | **5** | Garcia Taboada Brayan Albaro | Terminada |
| 16 | Pb-23 | Liberar bloqueo desde el panel | Media | M6 | Pb-6, Pb-22 | **3** | Garcia Taboada Brayan Albaro | Terminada |
| | | **Total de PHU** | | | | **77** | | 30 terminados; 5 implementados pendientes de VM |

### 2.1 Reparto por desarrollador

| Desarrollador | HU asignadas | PHU | Pendientes | Bloque de trabajo |
|---|---|---|---|---|
| Garcia Taboada Brayan Albaro | Pb-22, Pb-23, Pb-25, Pb-26 | **21** | 5 (solo evidencia VM de Pb-25) | Panel web: sesión, detalle de incidente, estado, tablero y liberación |
| Vargas Figueroa Jairo Moises | Pb-15, Pb-29, Pb-19, Pb-24 | **19** | 8 aplazados (Pb-19) | Borde de entrada y alertas terminados; IA local aplazada |
| Soldado Capuma Brandon | Pb-16, Pb-17 | **13** | 13 | Ciclo de vida del baneo: reincidencia y fuerza bruta |
| Sandoval Martinez Erick | Pb-13, Pb-14, Pb-18 | **13** | 13 | Escaneo y sondeo de archivos, más la lista blanca administrable |
| Aldana Claure Brayan | Pb-11, Pb-12, Pb-21 | **11** | 8 | Historial terminado; pendientes las firmas XSS y path traversal |

**Criterio del reparto.** El equipo decidió concentrar en dos desarrolladores las HU con dependencias externas o de mayor volumen —el borde de entrada y la IA local en Vargas, el grueso del panel web en Garcia— y repartir entre los otros tres el trabajo de firmas, motor de políticas y API, que es más homogéneo y no depende de componentes de terceros.

### 2.2 Cadena de dependencias del panel (M6)

La revisión durante el desarrollo mostró que varias dependencias eran necesarias para **cerrar** las HU, pero no para empezar su interfaz. La cadena efectiva quedó así:

| HU del panel | Espera a | De quién | Tipo |
|---|---|---|---|
| Pb-22 | **Pb-21** (filtros de `GET /api/incidentes`) | Aldana | Bloqueante solo para el cierre; la estructura visual pudo avanzar antes |
| Pb-24 | Sesión web y lista de incidentes de Pb-22 | Garcia | Compartió el cimiento de autenticación, no el detalle completo |
| Pb-23 | Sesión web | Garcia | No necesitó esperar los filtros de Pb-21 |
| Pb-25 | Configuración opcional de Ollama | Vargas | No bloqueante: muestra `no_configurado` mientras Pb-19 esté aplazada |
| Pb-26 | Pb-11 a Pb-14 (tipos de ataque) | Aldana, Sandoval | Blando: el gráfico funciona, pero muestra una sola categoría |
| Pb-22 | Pb-19 (etiqueta «generado por IA») | Vargas | Blando: hasta entonces todo sale como «plantilla» |
| Pb-23 | Pb-16 (nivel de reincidencia visible) | Soldado | Blando: el dato se muestra vacío hasta que exista |

**Camino aplicado:** sesión web + Pb-21 → Pb-22, mientras Pb-23, Pb-25 y Pb-26 avanzaron en paralelo. Pb-24 reutilizó la sesión por cookie y el listado, pero no necesitó esperar al detalle completo.

**Dos autores sobre `panel.html`.** Pb-24 queda en Vargas y el resto del panel en Garcia, así que ambos editan `servicio/app/web/templates/panel.html` y `static/js/panel.js`. Conviene acordar de antemano que Pb-24 solo toca el bloque `#incidentes` y su script, para no chocar con el resto de la plantilla.

**Resultado de la separación.** `GET /api/salud` y `GET /api/metricas` se implementaron como endpoints independientes de las plantillas. Esto permitió probar el backend y la interfaz por separado y dejó a Pb-25 pendiente únicamente de su evidencia sobre la VM real.

Todas figuran como Media en el Product Backlog original (`docs/sprint 0.md`); a diferencia del Sprint 1, aquí no se propone subir ninguna a Alta porque el ciclo completo (detectar → bloquear → explicar → notificar → liberar) ya cierra desde el Sprint 1. El Product Owner confirma si alguna debe subir de prioridad.

---

## 3. Objetivo del Sprint 2

> Completar el Product Backlog: ampliar la detección a los cinco tipos de ataque restantes del MVP, refinar la respuesta (bloqueo progresivo, fuerza bruta, lista blanca administrable), enriquecer el borde con límite de tasa y HTTPS, mejorar el informe con IA local (Ollama) y entregar el panel web completo como segundo canal de operación, con las mismas garantías de auditoría, disponibilidad y operación sin conexión que el Sprint 1.

### 3.1 Qué queda operativo al final del sprint

1. La plataforma detecta y descarta, además de inyección SQL, XSS, path traversal, escaneo/reconocimiento y sondeo de archivos sensibles, todos sobre la misma tubería de Suricata y el mismo correlador.
2. Un atacante reincidente recibe bloqueos cada vez más largos (10 min, 20 min, 40 min... hasta 24 h), y su incidente puede alcanzar severidad crítica.
3. Un intento de fuerza bruta contra el login también termina en un incidente auditable, aunque el baneo lo decida Fail2ban sin pasar por Suricata.
4. El administrador administra la lista blanca por API, sin editar archivos de configuración en el servidor.
5. El borde de la plataforma limita la tasa de peticiones por IP y puede terminar TLS, inspeccionando tráfico cifrado.
6. El informe del incidente lo redacta un modelo de lenguaje local (Ollama) cuando puede, con la plantilla como respaldo automático y la etiqueta de origen siempre visible.
7. El administrador puede hacer todo lo que hace en el móvil también desde el panel web: ver el tablero, las alertas en vivo, el estado de los componentes, el detalle de cada incidente y liberar bloqueos.
8. El historial de incidentes se filtra por fecha, origen y severidad, en la API y en el panel.

### 3.2 Fuera del incremento

| Elemento | Motivo |
|---|---|
| Gateway multiaplicación (registrar varias aplicaciones protegidas en caliente) | Declarado como visión y ampliación en el documento de contexto, nunca entró al Product Backlog |
| Consulta por voz sobre el estado ("¿qué pasó anoche?") | Ampliación valorada, no HU del Product Backlog |
| Biometría (`local_auth`) antes de liberar un bloqueo | Propuesta opcional dentro de Pb-28 (Sprint 1); no es obligatoria |
| Recuperación de contraseña / múltiples usuarios administradores | Fuera de alcance del MVP (decisión abierta de Pb-1, Sprint 1) |

Con este sprint se cierran las 29 historias del Product Backlog; no queda HU pendiente para un tercer sprint.

---

## 4. Detalle de las historias de usuario (tarjetas F4)

Mismos campos que en el Sprint 1: identificador, nombre corto, prioridad, PHU, Como / Quiero / Para, criterios de aceptación y conversación (opcional).

### Pb-15. Límite de tasa

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-15 | Límite de tasa | Media | **3** | Terminada |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | limitar las peticiones por segundo desde una misma IP |
| **Para** | frenar ráfagas y sondeos masivos antes de que lleguen a la aplicación |
| Módulo y requisitos | M1 · RF-02 |
| Depende de | Cimientos de enrutamiento (C-14, C-15) |

**Criterios de Aceptación**

1. nginx aplica `limit_req` sobre la IP real (tras `real_ip_header`): 10 req/s por IP con ráfaga de 20, y un límite más estricto para el login (propuesta: 5 req/min), según los valores orientativos del documento de contexto.
2. Al superar el límite, nginx responde 429 sin que la petición llegue a la aplicación protegida.
3. Se limita la IP real del cliente, no la del proxy.
4. Una sesión prolongada de navegación legítima (propuesta: 10 minutos con navegador y k6) no recibe ningún 429.
5. El límite se mide con k6 y se documenta junto a la latencia añadida por Suricata (Pb-3), para no confundir ambas causas de rechazo.
6. Se documenta la diferencia con el bloqueo de Pb-6: este límite es volumétrico y vive en nginx; el de Pb-6 depende de eventos maliciosos y vive en el motor de políticas.

**Conversación / Reglas (opcional)**

- Los valores son iniciales y se calibran en las pruebas, igual que el resto de umbrales del sistema.
- No sustituye a Fail2ban ni al motor de políticas: es una primera barrera contra ráfagas, no una detección de ataque.

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Vargas Figueroa Jairo Moises |
|---|---|

---

### Pb-29. Terminación TLS

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-29 | Terminación TLS | Media | **5** | Terminada |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | que el punto de entrada termine el cifrado HTTPS |
| **Para** | que el contenido de las peticiones cifradas pueda inspeccionarse |
| Módulo y requisitos | M1 · RF-01 |
| Depende de | Pb-15; cimientos de enrutamiento (C-14, C-15) |

**Criterios de Aceptación**

1. nginx sirve HTTPS con un certificado del laboratorio (autofirmado o `mkcert`) y sigue reenviando a la aplicación protegida por HTTP en el tramo interno (Modo B).
2. Un ataque de sqlmap sobre HTTPS genera las mismas alertas en `eve.json` que sobre HTTP en claro, porque Suricata inspecciona el tramo ya descifrado.
3. Los certificados y las claves privadas no están en el repositorio; una búsqueda de secretos no los encuentra.
4. Se documenta si HTTP en claro queda deshabilitado o redirige a HTTPS, y el efecto sobre la app móvil (que hoy usa HTTP plano, Pb-8).
5. La latencia añadida por el cifrado se mide con k6 y se compara contra el Modo A (HTTP) del Sprint 1.
6. El límite de tasa de Pb-15 sigue aplicándose igual en HTTPS.

**Conversación / Reglas (opcional)**

- El documento de contexto declara el Modo A (HTTP en claro) como limitación del MVP del Sprint 1 y difiere el Modo B a esta HU.
- Pasar la app móvil a HTTPS con un certificado no confiable de laboratorio puede requerir configuración adicional en Android; si no se resuelve en este sprint, se documenta como limitación.

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Vargas Figueroa Jairo Moises |
|---|---|

---

### Pb-11. Detección de XSS

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-11 | Detección de XSS | Media | **5** | Pendiente |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | que los intentos de XSS enviados por URI o cuerpo se detecten y registren |
| **Para** | identificar ataques dirigidos a los usuarios del sitio |
| Módulo y requisitos | M2 · RF-03 |
| Depende de | Pb-2, Pb-3 (misma tubería) |

**Criterios de Aceptación**

1. Un payload reflejado típico de XSS enviado por parámetro GET o por cuerpo POST genera una alerta en `eve.json` con categoría `xss`.
2. El evento se guarda y se agrupa en un incidente (Pb-5) con `tipo_ataque = xss`.
3. Las firmas de XSS de alta confianza se agregan a `drop.conf`, reutilizando el mecanismo de descarte de Pb-3.
4. El XSS por fragmento `#` de la URL (propio de una SPA) no llega al servidor y no se detecta; queda documentado como límite conocido, igual que en el documento de contexto.
5. Una sesión de navegación legítima no genera alertas de XSS.
6. Prueba con `curl` o ZAP contra un parámetro reflejado de la aplicación de la demostración.
7. La categoría OWASP asignada en el informe (Pb-7) para `xss` queda configurada en la tabla de categorías, sin tocar el generador.

**Conversación / Reglas (opcional)**

- Se combinan firmas de Emerging Threats Open (categorías web) con una regla propia, igual que para inyección SQL en Pb-2.

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Aldana Claure Brayan |
|---|---|

---

### Pb-12. Detección de path traversal

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-12 | Detección de path traversal | Media | **3** | Pendiente |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | que los intentos de acceder a rutas fuera del directorio permitido se detecten y registren |
| **Para** | evitar la lectura de archivos del servidor |
| Módulo y requisitos | M2 · RF-03 |
| Depende de | Pb-2, Pb-3 |

**Criterios de Aceptación**

1. Una petición con un patrón de traversal (`../../etc/passwd` y variantes con codificación porcentual) coincide con una firma y genera una alerta de categoría `traversal`.
2. El evento se agrupa en un incidente con `tipo_ataque = traversal` y categoría OWASP A01 (a verificar, según el mapeo inicial del documento de contexto).
3. Una doble codificación del patrón se prueba explícitamente; si evade la firma, se documenta como límite de inspección, sin bloquear el resto del sprint.
4. Prueba con `curl` o `ffuf` contra rutas fuera del directorio permitido de la aplicación de la demostración.
5. La navegación legítima de prueba no genera falsos positivos de esta categoría.
6. Las firmas de alta confianza quedan en `drop.conf` para descartar antes de llegar a la aplicación.

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Aldana Claure Brayan |
|---|---|

---

### Pb-13. Detección de escaneo

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-13 | Detección de escaneo | Media | **5** | Pendiente |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | que el escaneo y reconocimiento automatizado (Nikto, ffuf) se detecte y registre |
| **Para** | actuar contra quien busca vulnerabilidades antes de que las encuentre |
| Módulo y requisitos | M2 · RF-03 |
| Depende de | Pb-2, Pb-3, Pb-6 (para el bloqueo tras superar el umbral) |

**Criterios de Aceptación**

1. Un escaneo con Nikto o ffuf genera múltiples alertas de categoría `escaneo`.
2. Los eventos de un mismo escaneo se agrupan en un único incidente por IP dentro de la ventana de 5 minutos (Pb-5), sin saturar la ingesta pese a cientos de peticiones.
3. Si el escaneo supera el umbral de eventos de Pb-6, la IP se bloquea automáticamente, sin agregar lógica nueva al motor de políticas.
4. La navegación legítima con muchas páginas (por ejemplo, paginación de un catálogo) no se confunde con escaneo.
5. Prueba documentada según el plan de pruebas del documento de contexto: "escaneo de rutas con Nikto/ffuf → baneo tras superar el umbral".

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Sandoval Martinez Erick |
|---|---|

---

### Pb-14. Detección de sondeo de archivos sensibles

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-14 | Detección de sondeo de archivos sensibles | Media | **3** | Pendiente |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | que los intentos de acceder a archivos de configuración o respaldo (`.env`, `.git`, copias) se detecten y registren |
| **Para** | evitar la fuga de credenciales |
| Módulo y requisitos | M2 · RF-03 |
| Depende de | Pb-2, Pb-3 |

**Criterios de Aceptación**

1. Peticiones a rutas típicas de archivos sensibles (`.env`, `.git/config`, copias `.bak`, `wp-config.php.bak`, etc.) generan una alerta de categoría `sondeo_archivos`.
2. El evento se agrupa como incidente con `tipo_ataque = sondeo_archivos` (valor ya admitido por el esquema de datos).
3. Se decide y documenta si el clasificador local (Pb-20) reconoce `sondeo_archivos` como clase propia o la mapea a `escaneo`, cerrando la decisión abierta 3 de `Modelo_datos.md`.
4. La reincidencia de sondeos puede derivar en un bloqueo si supera el umbral de Pb-6, sin lógica adicional.
5. Prueba con `curl` contra una lista de rutas sensibles conocidas de la aplicación de la demostración.

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Sandoval Martinez Erick |
|---|---|

---

### Pb-16. Bloqueo progresivo

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-16 | Bloqueo progresivo | Media | **5** | Pendiente |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | que cada reincidencia duplique la duración del bloqueo |
| **Para** | mantener fuera más tiempo a los atacantes persistentes |
| Módulo y requisitos | M3 · RF-05 |
| Depende de | Pb-6 |

**Criterios de Aceptación**

1. La duración de un baneo es `10 minutos × 2^nivel_reincidencia`, con tope de 24 horas (regla ya prevista en el campo `baneo.nivel_reincidencia` del esquema de datos).
2. `nivel_reincidencia` se calcula a partir de los baneos anteriores de la misma IP; se documenta si un baneo liberado manualmente cuenta o no como reincidencia.
3. Esta HU implementa la escala de severidad invertida documentada como diseño objetivo (`incidente.severidad`: 1 baja a 4 crítica) y cierra la brecha registrada en `Modelo_datos.md`: hoy el código propaga la severidad de la firma sin invertirla y sin llegar a 4.
4. La severidad **crítica** (4) se asigna cuando el incidente es de severidad alta y la IP reincide.
5. Al alcanzar el tope de 24 horas, los baneos siguientes de esa IP mantienen esa duración máxima, sin seguir duplicando.
6. El nivel de reincidencia queda visible en el detalle del baneo y auditado.
7. Prueba: una misma IP reincidente encadena baneos de 10, 20 y 40 minutos.

**Conversación / Reglas (opcional)**

- Esta HU es la que habilita la severidad crítica que Pb-10 (notificaciones, Sprint 1) ya contempla en su regla de negocio pero que hasta ahora nunca podía ocurrir.

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Soldado Capuma Brandon |
|---|---|

---

### Pb-17. Bloqueo por fuerza bruta

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-17 | Bloqueo por fuerza bruta | Media | **8** | Pendiente |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | que las IP con intentos fallidos repetidos de inicio de sesión se bloqueen |
| **Para** | proteger las cuentas de los clientes |
| Módulo y requisitos | M3 · RF-05 |
| Depende de | Pb-1 (login), Pb-6 |

**Criterios de Aceptación**

1. Un filtro de Fail2ban sobre `access.log` detecta 5 respuestas 401/403 al login en 60 segundos desde la misma IP.
2. Al superar el umbral, Fail2ban banea la IP en nftables, reutilizando la infraestructura de bloqueo de Pb-6.
3. El servicio se entera del baneo hecho por Fail2ban (que no pasa por Suricata) y crea o asocia un incidente con `tipo_ataque = fuerza_bruta`, resolviendo la decisión abierta 1 de `Modelo_datos.md` sobre cómo satisfacer que `baneo.incidente_id` sea obligatorio en este caso.
4. El incidente resultante sigue el mismo ciclo de vida que cualquier otro: tiene informe (Pb-7/Pb-19) y notifica si su severidad es alta (Pb-10).
5. Una IP de la lista blanca nunca se banea por este filtro.
6. Prueba con el script propio de fuerza bruta contra `POST /api/auth/login`.
7. El baneo resultante se libera igual que cualquier otro, desde el móvil (Pb-28) o el panel (Pb-23).

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Soldado Capuma Brandon |
|---|---|

---

### Pb-18. Gestión de lista blanca

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-18 | Gestión de lista blanca | Media | **5** | Pendiente |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | consultar, agregar y quitar direcciones de la lista blanca |
| **Para** | adaptar las excepciones a mi red sin tocar la configuración del servidor |
| Módulo y requisitos | M3 · RF-06 |
| Depende de | Pb-6; cimiento de lista blanca por defecto (C-22) |

**Criterios de Aceptación**

1. `GET /api/lista-blanca` (autenticado) devuelve las entradas, marcando las predeterminadas (loopback, red de administración, gateway) como no editables.
2. `POST /api/lista-blanca` agrega una IP o red en notación CIDR, validada con la librería de direcciones IP antes de guardar; un valor inválido se rechaza sin tocar la base.
3. `DELETE /api/lista-blanca/{id}` quita una entrada que no sea predeterminada.
4. El motor de políticas de Pb-6 consulta esta tabla en cada decisión de bloqueo, cerrando la brecha de `Modelo_datos.md`: hoy la tabla existe pero ningún componente la lee ni la escribe, y la exclusión real usa una variable de entorno.
5. Un intento de banear una IP que está en la lista blanca sigue generando solo alerta, nunca un baneo.
6. Toda alta o baja se audita (actor, fecha, IP o red afectada).
7. Las entradas predeterminadas se siembran al arrancar el servicio si todavía no existen.

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

| Desarrollador | Sandoval Martinez Erick |
|---|---|

---

### Pb-19. Informe con IA local

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-19 | Informe con IA local | Media | **8** | Aplazada por decisión del equipo |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | que el informe del incidente lo redacte un modelo de lenguaje local |
| **Para** | obtener explicaciones más claras sin depender de la nube |
| Módulo y requisitos | M5 · RF-10 (y RNF-03 como criterio) |
| Depende de | Pb-7; cimiento de Ollama (C-32); spike 5 (C-43) |

**Criterios de Aceptación**

1. El generador de informes llama a un modelo local servido por Ollama (de 1 a 3 B de parámetros) con un prompt que solo contiene los hechos del incidente.
2. Si Ollama responde con las cuatro secciones esperadas (qué ocurrió, categoría OWASP, acción aplicada, recomendaciones) dentro de 20 segundos, el informe se guarda con `origen_informe = generado_ia` y el nombre del modelo en `modelo_informe`.
3. Si Ollama tarda más de 20 segundos, no responde o la salida no trae las cuatro secciones, se usa `GeneradorPlantilla` como respaldo automático y `origen_informe = plantilla`, sin que el incidente se quede sin informe.
4. La app móvil (Pb-27) y el panel (Pb-22) muestran siempre la etiqueta "generado por IA" o "plantilla" según `origen_informe`.
5. El contenido capturado de la petición se envía al modelo como dato delimitado y truncado; su salida nunca se interpreta como instrucción ni ejecuta ninguna acción.
6. Funciona sin conexión a internet: Ollama corre en el equipo anfitrión y la VM lo consulta por la red host-only.
7. Se documenta la relación con `GeneradorOpenRouter`: el cliente y sus pruebas existen, pero el arranque actual usa `GeneradorPlantilla`; cuando se retome esta HU, Ollama debe pasar a ser el generador local principal.
8. Prueba: una muestra de incidentes genera informe válido con Ollama en menos de 20 s en la máquina de la demostración, o se documenta la decisión de usar un modelo más pequeño (criterio del spike 5).

**Prototipo / Mockup (opcional)**

No aplica: el informe se muestra en la app móvil (Pb-27) y en el panel (Pb-22); esta HU solo cambia quién lo redacta.

| Desarrollador | Vargas Figueroa Jairo Moises |
|---|---|

---

### Pb-21. Historial consultable

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-21 | Historial consultable | Media | **3** | Terminada |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | consultar el historial de incidentes filtrando por fecha, origen y severidad |
| **Para** | investigar lo ocurrido en un período |
| Módulo y requisitos | M4 · RF-08 |
| Depende de | Pb-5 |

**Criterios de Aceptación**

1. `GET /api/incidentes` acepta filtros opcionales y combinables por rango de fecha, IP de origen y severidad.
2. Sin filtros, el endpoint se comporta igual que en el Sprint 1 (compatible con Pb-5 y Pb-27).
3. La respuesta queda paginada o acotada, para no devolver miles de incidentes de una vez.
4. Los filtros se resuelven en la base de datos, apoyados en los índices existentes (`ix_incidente_ip_origen`, `ix_incidente_ultima_actividad`), sin degradar el tiempo de respuesta.
5. Un filtro con formato inválido (fecha o IP) responde 400 con un mensaje claro y no ejecuta la consulta.
6. Sin token responde 401, igual que hoy.
7. Prueba: filtrar por un rango de fecha y una IP concreta devuelve exactamente los incidentes esperados.

**Prototipo / Mockup (opcional)**

No aplica: es una HU sin interfaz. La evidencia de la demostración es la prueba documentada en `pruebas/`.

**Resultado del desarrollo (20/09/2026).** Se agregaron `desde`, `hasta`, `ip_origen` y
`severidad` como filtros combinables sobre `ultima_actividad`, conservando `limite` y
`desplazamiento`. Las fechas aceptan ISO 8601 y se normalizan a UTC; fecha, rango, IP o severidad
inválidos responden 400. La prueba automática verifica una combinación de fecha, IP y severidad.
Evidencia: `pruebas/evidencias/Pb-21.md`.

| Desarrollador | Aldana Claure Brayan |
|---|---|

---

### Pb-22. Detalle de incidente (panel)

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-22 | Detalle de incidente (panel) | Media | **8** | Terminada |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | abrir un incidente y ver sus eventos y su informe, indicando si es "generado por IA" o "plantilla" |
| **Para** | decidir qué hacer |
| Módulo y requisitos | M6 · RF-11 |
| Depende de | Pb-5, Pb-7, Pb-21; esqueleto del panel (C-33) |

**Criterios de Aceptación**

1. El panel muestra la lista de incidentes (reutilizando los filtros de Pb-21) con IP, tipo de ataque, severidad y estado, el más reciente primero.
2. Al abrir un incidente se ve su informe completo con las cuatro secciones y la etiqueta de origen (`plantilla` o `generado_ia`).
3. Se listan los eventos del incidente, con los datos capturados de la petición como texto plano truncado, nunca interpretados como código.
4. Si el incidente todavía no tiene informe, el panel lo indica sin fallar (mismo comportamiento que Pb-27 en el móvil).
5. Sin sesión válida, el panel exige iniciar sesión antes de mostrar cualquier dato.
6. La página se sirve desde el propio servicio (Jinja2 + HTMX, sin CDN) y funciona sin conexión a internet.

**Prototipo / Mockup (opcional)**

Esqueleto existente: `servicio/app/web/templates/panel.html`, bloque `#incidentes`.

**Resultado del desarrollo (20/09/2026).** El panel exige una sesión web en cookie `HttpOnly`,
muestra la tabla filtrable y abre un diálogo con resumen, ficha y eventos. Todo dato capturado se
inserta con `textContent`, nunca como HTML. La ausencia de informe se presenta como estado de
espera. Se verificó visualmente en modo simulado y mediante pruebas automáticas. Evidencia:
`pruebas/evidencias/Pb-22.md`.

| Desarrollador | Garcia Taboada Brayan Albaro |
|---|---|

---

### Pb-25. Estado de componentes (panel)

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-25 | Estado de componentes (panel) | Media | **5** | Implementada; verificación VM pendiente |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | ver si nginx, Suricata, Fail2ban y Ollama están operativos |
| **Para** | saber cuándo la defensa está degradada |
| Módulo y requisitos | M6 · RF-11 |
| Depende de | Pb-4 (`GET /api/salud`); esqueleto del panel (C-33) |

**Criterios de Aceptación**

1. El panel muestra el estado de nginx, Suricata, Fail2ban y Ollama, ampliando `GET /api/salud` de Pb-4.
2. Con Suricata detenido, el panel lo marca como degradado, con el mismo criterio que ya usa Pb-4.
3. Si Ollama no responde, el panel lo marca como degradado y el informe se sigue generando con la plantilla (Pb-19), sin que el panel deje de cargar.
4. El estado se refresca sin recargar toda la página.
5. Sin sesión válida, no se muestra el estado.
6. Prueba: detener Suricata con `systemctl stop` y verificar que el panel refleja el cambio.

**Prototipo / Mockup (opcional)**

Esqueleto existente: `panel.html`, bloque `#componentes` (lista con los cuatro componentes ya maquetada).

**Resultado del desarrollo (20/09/2026).** `GET /api/salud` informa por separado nginx,
Suricata, Fail2ban y Ollama. En modo simulado los servicios del host aparecen como `no_aplica` y,
mientras Pb-19 esté aplazada, Ollama aparece como `no_configurado`. Si se define
`DEFENSA_OLLAMA_URL`, se comprueba `/api/tags`; una caída devuelve `inactivo` y degrada el estado
global. El panel refresca cada 30 s y bajo demanda. Falta ejecutar el criterio 6 deteniendo
Suricata en la VM; hasta registrar esa evidencia la HU no se considera terminada. Evidencia:
`pruebas/evidencias/Pb-25.md`.

| Desarrollador | Garcia Taboada Brayan Albaro |
|---|---|

---

### Pb-24. Alertas en tiempo real (panel)

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-24 | Alertas en tiempo real (panel) | Media | **3** | Terminada |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | ver las alertas en el panel apenas ocurren |
| **Para** | reaccionar sin refrescar la página |
| Módulo y requisitos | M6 · RF-11 |
| Depende de | Pb-5, Pb-22 |

**Criterios de Aceptación**

1. `GET /api/eventos` (autenticado, SSE) transmite cada incidente nuevo apenas se persiste, sin esperar la generación de su ficha. El endpoint existente se completó durante esta HU.
2. El panel, abierto con una sesión válida, muestra la alerta sin recargar la página.
3. Si se corta la conexión SSE, el panel reintenta automáticamente sin perder alertas.
4. La conexión respeta la autenticación: se corta si el token vence.
5. La transmisión es asíncrona y nunca frena la lectura ni la correlación de eventos.
6. Prueba: un ataque en curso aparece en el panel abierto sin refrescar; meta de laboratorio: no más de 2 s desde que el servicio persiste el incidente.

**Conversación / Reglas (opcional)**

- La conexión usa la cookie de sesión del panel o Bearer para clientes que lo soporten. Cada alerta lleva `id`; al reconectar se usa `Last-Event-ID` y SQLite para reponer incidentes omitidos.

**Prototipo / Mockup (opcional)**

Esqueleto existente: `panel.html`, bloque `#incidentes`; el estilo de alerta entrante se define en `panel.css`.

**Resultado del desarrollo (20/09/2026).** El panel presenta un aviso accesible sin recargar,
actualiza historial, métricas y bloqueos, y reconecta automáticamente. La alerta se publica justo
después de persistir el incidente y antes de generar el informe, por lo que Pb-19 no añade latencia
al canal. El servidor repone desde SQLite todos los incidentes posteriores al último identificador
recibido y finaliza el flujo al vencer el JWT. La prueba visual en modo simulado mostró la alerta y
el incremento de métricas de forma inmediata. Evidencia: `pruebas/evidencias/Pb-24.md`.

| Desarrollador | Vargas Figueroa Jairo Moises |
|---|---|

---

### Pb-26. Tablero de métricas (panel)

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-26 | Tablero de métricas (panel) | Media | **5** | Terminada |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | un tablero con incidentes por hora, bloqueos vigentes, tipos de ataque y top de IPs |
| **Para** | evaluar la situación de un vistazo |
| Módulo y requisitos | M6 · RF-11 |
| Depende de | Pb-5, Pb-6, Pb-20; esqueleto del panel (C-33) |

**Criterios de Aceptación**

1. `GET /api/metricas` (autenticado) expone incidentes por hora, bloqueos vigentes, distribución por tipo de ataque y el top de IPs de origen.
2. El panel dibuja estos datos con Chart.js, servido desde archivos locales, sin CDN.
3. Las métricas se calculan sobre incidentes y baneos ya existentes en la base, sin agregar tablas nuevas.
4. El tablero se actualiza sin recargar toda la página.
5. Sin sesión válida, responde 401.
6. Prueba: tras una ráfaga de sqlmap seguida de un baneo, el tablero refleja el incremento de incidentes y de bloqueos vigentes.

**Prototipo / Mockup (opcional)**

Esqueleto existente: `panel.html`, `rejilla-metricas` y el `<canvas id="grafico-incidentes">` ya reservado para Chart.js.

**Resultado del desarrollo (20/09/2026).** `GET /api/metricas` entrega resumen del día UTC,
bloqueos vigentes, 24 intervalos horarios, distribución completa por tipo y top 5 de IPs. Las
agregaciones se hacen sobre SQLite sin tablas nuevas. El panel usa Chart.js local y se actualiza
cada 30 s o al recibir SSE. Evidencia: `pruebas/evidencias/Pb-26.md`.

| Desarrollador | Garcia Taboada Brayan Albaro |
|---|---|

---

### Pb-23. Liberar bloqueo desde el panel

| Id. | Nombre corto de HU | Prioridad | HU (PHU) | Estado |
|---|---|---|---|---|
| Pb-23 | Liberar bloqueo desde el panel | Media | **3** | Terminada |

| Campo | Detalle |
|---|---|
| **Como** | administrador de seguridad |
| **Quiero** | liberar una IP bloqueada desde el panel web |
| **Para** | corregir un falso positivo sin usar la consola del servidor |
| Módulo y requisitos | M6 · RF-06, RF-12 |
| Depende de | Pb-6, Pb-22 |

**Criterios de Aceptación**

1. El panel lista los bloqueos vigentes (`GET /api/baneos`) con IP, incidente asociado y hora de expiración.
2. El panel pide confirmación explícita antes de liberar.
3. Al confirmar, la regla desaparece de `nft list ruleset` y el baneo pasa a `liberado`, reutilizando `POST /api/baneos/{ip}/liberar`.
4. Liberar una IP que ya no está bloqueada no produce error (operación idempotente, igual que Pb-28).
5. La liberación se audita con usuario, fecha e IP afectada.
6. Un valor de IP inválido se rechaza sin ejecutar ningún comando.
7. Sin sesión válida, la acción responde 401.
8. Tras liberar, la lista del panel se actualiza sin recargar toda la página.

**Conversación / Reglas (opcional)**

- Es la contraparte web de Pb-28 (liberar desde el móvil, Sprint 1): mismos endpoints, misma auditoría, otra interfaz.

**Prototipo / Mockup (opcional)**

Bloque nuevo en `panel.html`: lista de bloqueos vigentes con diálogo de confirmación antes de liberar.

**Resultado del desarrollo (20/09/2026).** `GET /api/baneos?estado=vigente` excluye baneos
expirados, el panel muestra la información operativa y exige confirmación en un diálogo nativo.
La acción reutiliza el endpoint idempotente existente, conserva su validación y auditoría y
actualiza lista y métricas sin recargar. La API de liberación quedó cubierta por prueba automática
y el diálogo se verificó visualmente. Evidencia: `pruebas/evidencias/Pb-23.md`.

| Desarrollador | Garcia Taboada Brayan Albaro |
|---|---|

---

## 5. Pendientes que llegan del Sprint 1 y siguen abiertos

| # | Pendiente | Dónde se originó | Relevancia para el Sprint 2 |
|---|---|---|---|
| 1 | ~~PHU de las 16 HU y capacidad del equipo~~ **Cerrado** | `Sprint1_Cimientos_y_Tarjetas_HU.md`, sección 5.2 | Estimado con Planning Poker: 77 PHU repartidos en la sección 2.1. Queda abierta la **velocidad real del equipo**, que solo se conoce al cerrar el sprint |
| 2 | Umbral aceptable de latencia añadida (RNF-02) | `Sprint1_Cimientos_y_Tarjetas_HU.md`, sección 5.2 | Pb-15 y Pb-29 vuelven a medir latencia con k6; es el momento de fijar el valor con los datos de ambos sprints |
| 3 | Decisión abierta 1 de `Modelo_datos.md`: cómo se entera el servicio de un baneo hecho por Fail2ban sin pasar por Suricata | `Modelo_datos.md`, sección 11 | La resuelve Pb-17 |
| 4 | Decisión abierta 3 de `Modelo_datos.md`: si `sondeo_archivos` es una clase propia del clasificador o se mapea a `escaneo` | `Modelo_datos.md`, sección 11 | La resuelve Pb-14 |
| 5 | Ubicación de Ollama una vez implementado | Documento de contexto, sección 13 | La resuelve Pb-19 (propuesta por defecto: equipo anfitrión, consultado desde la VM) |
