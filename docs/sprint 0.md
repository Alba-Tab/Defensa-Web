# Plataforma de Defensa Web en Tiempo de Ejecución
## Sprint 0: Product Backlog y Sprint Backlog por módulos

| Campo | Detalle |
|---|---|
| Proyecto | Plataforma de Defensa Web en Tiempo de Ejecución |
| Materia | Ingeniería de Software II, UAGRM |
| Grupo | 13 |
| Tema | Pruebas web con enfoque de defensa (sombrero blanco) |
| Proceso | Scrum |
| Product Owner | **[POR DEFINIR]** |
| Scrum Master | **[POR DEFINIR]** |
| Versión | 1.0 (borrador para validación del Product Owner) |
| Fecha | 18 de septiembre de 2026 |

> **Estado del documento.** Las prioridades son una propuesta hasta que las confirme el Product Owner. Los Puntos de Historia de Usuario (PHU) no se incluyen: los estima el equipo con Planning Poker. El Sprint Backlog es una propuesta que el equipo confirma en el Sprint Planning.

---

## 1. Product Backlog (F3)

Lista completa y ordenada de las 29 historias de usuario del proyecto. El orden es el de ejecución: cada HU depende solo de las anteriores. El nombre del proyecto, el Product Owner, la versión y la fecha del backlog son los del encabezado. Las prioridades son una propuesta y los PHU no se incluyen.

### 1.1 Rebanada vertical (primer corte candidato)

Es el hilo mínimo: ataque, detección, incidente, baneo, informe y notificación. Pb-1 a Pb-7 forman el servicio, demostrable por API y base de datos; Pb-8 a Pb-10 agregan el móvil.

| ID | Nombre corto | Historia | Prioridad | Módulo | RF |
|---|---|---|---|---|---|
| Pb-1 | Inicio de sesión | Como administrador de seguridad, quiero autenticarme para acceder a la API, al panel y a la app, para que solo personal autorizado vea incidentes o modifique bloqueos. | Alta | M4 | RF-08, RNF-04 |
| Pb-2 | Detección de inyección SQL | Como administrador de seguridad, quiero que las peticiones con patrones de inyección SQL se detecten y queden registradas como eventos estructurados (fecha, IP, firma, categoría, URL), para identificar el ataque cuando ocurre y poder auditarlo. | Alta | M2 | RF-03, RF-04 |
| Pb-3 | Descarte de peticiones maliciosas | Como administrador de seguridad, quiero que las peticiones que coincidan con firmas de alta confianza se descarten antes de llegar a la aplicación, para evitar el daño y no solo registrarlo. | Alta | M2 | RF-03 |
| Pb-4 | Continuidad ante falla | Como cliente legítimo, quiero seguir accediendo a la aplicación aunque el motor de inspección se detenga, para que la defensa nunca sea la causa de una caída. | Alta | M2 | RNF-01 |
| Pb-5 | Agrupación en incidentes | Como administrador de seguridad, quiero que los eventos de una misma IP y categoría se agrupen en un incidente, para ver un ataque como una unidad y no como cientos de líneas de log. | Alta | M4 | RF-07 |
| Pb-6 | Bloqueo temporal por umbral | Como administrador de seguridad, quiero que una IP que supere el umbral de eventos en una ventana de tiempo se bloquee temporalmente en el firewall, para cortar un ataque sostenido sin intervención manual. | Alta | M3 | RF-05, RF-02, RF-06, RNF-04 |
| Pb-7 | Informe desde plantilla | Como administrador de seguridad, quiero que cada incidente tenga un informe en lenguaje natural (qué ocurrió, categoría OWASP, acción aplicada, recomendaciones) generado desde una plantilla, para entenderlo sin ser experto en seguridad y sin depender de la IA. | Alta | M5 | RF-10 |
| Pb-8 | Conectar la app al servidor | Como administrador de seguridad, quiero configurar en la app la dirección del servidor e iniciar sesión, para consultar el sistema desde el celular. | Alta | M7 | RF-13 |
| Pb-9 | Registro del dispositivo | Como administrador de seguridad, quiero registrar mi dispositivo para recibir notificaciones, para que el servidor sepa a dónde enviar las alertas. | Alta | M7 | RF-13 |
| Pb-10 | Notificación de incidentes graves | Como administrador de seguridad, quiero recibir una notificación cuando un incidente sea de severidad alta o crítica, para enterarme aunque no esté frente al panel. | Alta | M7 | RF-13 |

### 1.2 Resto del backlog

| ID | Nombre corto | Historia | Prioridad | Módulo | RF |
|---|---|---|---|---|---|
| Pb-11 | Detección de XSS | Como administrador de seguridad, quiero que los intentos de XSS enviados por URI o cuerpo se detecten y registren, para identificar ataques dirigidos a los usuarios del sitio. | Media | M2 | RF-03 |
| Pb-12 | Detección de path traversal | Como administrador de seguridad, quiero que los intentos de acceder a rutas fuera del directorio permitido se detecten y registren, para evitar la lectura de archivos del servidor. | Media | M2 | RF-03 |
| Pb-13 | Detección de escaneo | Como administrador de seguridad, quiero que el escaneo y reconocimiento automatizado (Nikto, ffuf) se detecte y registre, para actuar contra quien busca vulnerabilidades antes de que las encuentre. | Media | M2 | RF-03 |
| Pb-14 | Detección de sondeo de archivos sensibles | Como administrador de seguridad, quiero que los intentos de acceder a archivos de configuración o respaldo (`.env`, `.git`, copias) se detecten y registren, para evitar la fuga de credenciales. | Media | M2 | RF-03 |
| Pb-15 | Límite de tasa | Como administrador de seguridad, quiero limitar las peticiones por segundo desde una misma IP, para frenar ráfagas y sondeos masivos. | Media | M1 | RF-02 |
| Pb-16 | Bloqueo progresivo | Como administrador de seguridad, quiero que cada reincidencia duplique la duración del bloqueo, para mantener fuera más tiempo a los atacantes persistentes. | Media | M3 | RF-05 |
| Pb-17 | Bloqueo por fuerza bruta | Como administrador de seguridad, quiero que las IP con intentos fallidos repetidos de inicio de sesión se bloqueen, para proteger las cuentas de los clientes. | Media | M3 | RF-05 |
| Pb-18 | Gestión de lista blanca | Como administrador de seguridad, quiero consultar, agregar y quitar direcciones de la lista blanca, para adaptar las excepciones a mi red sin tocar la configuración del servidor. | Media | M3 | RF-06 |
| Pb-19 | Informe con IA local | Como administrador de seguridad, quiero que el informe del incidente lo redacte un modelo de lenguaje local, para obtener explicaciones más claras sin depender de la nube. | Media | M5 | RF-10 |
| Pb-20 | Clasificación local | Como administrador de seguridad, quiero que un modelo entrenado localmente clasifique cada petición sospechosa por tipo de ataque y severidad, para priorizar incidentes sin depender de la nube. | Media | M5 | RF-09 |
| Pb-21 | Historial consultable | Como administrador de seguridad, quiero consultar el historial de incidentes filtrando por fecha, origen y severidad, para investigar lo ocurrido en un período. | Media | M4 | RF-08 |
| Pb-22 | Detalle de incidente | Como administrador de seguridad, quiero abrir un incidente y ver sus eventos y su informe, indicando si es "generado por IA" o "plantilla", para decidir qué hacer. | Media | M6 | RF-11 |
| Pb-23 | Liberar bloqueo desde el panel | Como administrador de seguridad, quiero liberar una IP bloqueada desde el panel web, para corregir un falso positivo sin usar la consola del servidor. | Media | M6 | RF-06, RF-12 |
| Pb-24 | Alertas en tiempo real | Como administrador de seguridad, quiero ver las alertas en el panel apenas ocurren, para reaccionar sin refrescar la página. | Media | M6 | RF-11 |
| Pb-25 | Estado de componentes | Como administrador de seguridad, quiero ver si nginx, Suricata, Fail2ban y Ollama están operativos, para saber cuándo la defensa está degradada. | Media | M6 | RF-11 |
| Pb-26 | Tablero de métricas | Como administrador de seguridad, quiero un tablero con incidentes por hora, bloqueos vigentes, tipos de ataque y top de IPs, para evaluar la situación de un vistazo. | Media | M6 | RF-11 |
| Pb-27 | Informe en el móvil | Como administrador de seguridad, quiero consultar el informe de un incidente desde la app, para evaluarlo en el momento. | Media | M7 | RF-13 |
| Pb-28 | Liberar bloqueo desde el móvil | Como administrador de seguridad, quiero liberar un bloqueo de forma remota desde la app, para corregir un falso positivo sin estar frente al equipo. | Media | M7 | RF-14 |
| Pb-29 | Terminación TLS | Como administrador de seguridad, quiero que el punto de entrada termine el cifrado HTTPS, para que el contenido de las peticiones cifradas pueda inspeccionarse. | Media | M1 | RF-01 |

La sección 3 presenta estas mismas historias agrupadas por módulo del sistema.

---

## 2. Actores

"Actor" significa quién interactúa con la plataforma, no un rol Scrum.

| Actor | Tipo | Participación | ¿Aparece en el "Como"? |
|---|---|---|---|
| Administrador de seguridad | Persona, usuario primario | Supervisa incidentes y libera bloqueos desde el panel web y el móvil | Sí, en casi todas las HU |
| Cliente legítimo | Persona, usuario indirecto | Usa la aplicación protegida; sufre un falso positivo o una caída | Solo en Pb-4 |
| Origen malicioso | Persona hostil, externa | Ataca la aplicación | No. Se usa en criterios de aceptación y en el plan de pruebas |
| Aplicación web protegida | Sistema externo | Recibe el tráfico limpio | No |
| Servicio Firebase Cloud Messaging (FCM) | Sistema externo | Entrega notificaciones | No |
| Repositorio Emerging Threats Open | Sistema externo | Fuente de firmas | No |

nginx, Suricata, Fail2ban, nftables y Ollama son contenedores del sistema, no actores.

---

## 3. Product Backlog por módulo

### 3.1 Resumen

| Módulo | Requisitos | Historias de usuario | Cantidad |
|---|---|---|---|
| M1. Enrutamiento | RF-01, RF-02 | Pb-15, Pb-29 | 2 |
| M2. Inspección y bloqueo en línea | RF-03, RF-04, RNF-01 | Pb-2, Pb-3, Pb-4, Pb-11 a Pb-14 | 7 |
| M3. Respuesta por dirección | RF-05, RF-06 | Pb-6, Pb-16, Pb-17, Pb-18 | 4 |
| M4. Correlación y persistencia | RF-07, RF-08, RNF-04 | Pb-1, Pb-5, Pb-21 | 3 |
| M5. IA local | RF-09, RF-10 | Pb-7, Pb-19, Pb-20 | 3 |
| M6. Panel web | RF-11, RF-12 | Pb-22 a Pb-26 | 5 |
| M7. Móvil | RF-13, RF-14 | Pb-8, Pb-9, Pb-10, Pb-27, Pb-28 | 5 |
| **Total** | | | **29** |

Los IDs siguen el orden del backlog: cada HU depende solo de las anteriores.

### 3.2 M1. Enrutamiento

| ID | Nombre corto | Historia | Prioridad | RF |
|---|---|---|---|---|
| Pb-15 | Límite de tasa | Como administrador de seguridad, quiero limitar las peticiones por segundo desde una misma IP, para frenar ráfagas y sondeos masivos. | Media | RF-02 |
| Pb-29 | Terminación TLS | Como administrador de seguridad, quiero que el punto de entrada termine el cifrado HTTPS, para que el contenido de las peticiones cifradas pueda inspeccionarse. | Media | RF-01 |

El proxy nginx y la resolución de la IP real del cliente no son HU: son tareas técnicas del Sprint Backlog (ver sección 4.2).

### 3.3 M2. Inspección y bloqueo en línea

| ID | Nombre corto | Historia | Prioridad | RF |
|---|---|---|---|---|
| Pb-2 | Detección de inyección SQL | Como administrador de seguridad, quiero que las peticiones con patrones de inyección SQL se detecten y queden registradas como eventos estructurados (fecha, IP, firma, categoría, URL), para identificar el ataque cuando ocurre y poder auditarlo. | Alta | RF-03, RF-04 |
| Pb-3 | Descarte de peticiones maliciosas | Como administrador de seguridad, quiero que las peticiones que coincidan con firmas de alta confianza se descarten antes de llegar a la aplicación, para evitar el daño y no solo registrarlo. | Alta | RF-03 |
| Pb-4 | Continuidad ante falla | Como cliente legítimo, quiero seguir accediendo a la aplicación aunque el motor de inspección se detenga, para que la defensa nunca sea la causa de una caída. | Alta | RNF-01 |
| Pb-11 | Detección de XSS | Como administrador de seguridad, quiero que los intentos de XSS enviados por URI o cuerpo se detecten y registren, para identificar ataques dirigidos a los usuarios del sitio. | Media | RF-03 |
| Pb-12 | Detección de path traversal | Como administrador de seguridad, quiero que los intentos de acceder a rutas fuera del directorio permitido se detecten y registren, para evitar la lectura de archivos del servidor. | Media | RF-03 |
| Pb-13 | Detección de escaneo | Como administrador de seguridad, quiero que el escaneo y reconocimiento automatizado (Nikto, ffuf) se detecte y registre, para actuar contra quien busca vulnerabilidades antes de que las encuentre. | Media | RF-03 |
| Pb-14 | Detección de sondeo de archivos sensibles | Como administrador de seguridad, quiero que los intentos de acceder a archivos de configuración o respaldo (`.env`, `.git`, copias) se detecten y registren, para evitar la fuga de credenciales. | Media | RF-03 |

### 3.4 M3. Respuesta por dirección

| ID | Nombre corto | Historia | Prioridad | RF |
|---|---|---|---|---|
| Pb-6 | Bloqueo temporal por umbral | Como administrador de seguridad, quiero que una IP que supere el umbral de eventos en una ventana de tiempo se bloquee temporalmente en el firewall, para cortar un ataque sostenido sin intervención manual. | Alta | RF-05, RF-02, RF-06, RNF-04 |
| Pb-16 | Bloqueo progresivo | Como administrador de seguridad, quiero que cada reincidencia duplique la duración del bloqueo, para mantener fuera más tiempo a los atacantes persistentes. | Media | RF-05 |
| Pb-17 | Bloqueo por fuerza bruta | Como administrador de seguridad, quiero que las IP con intentos fallidos repetidos de inicio de sesión se bloqueen, para proteger las cuentas de los clientes. | Media | RF-05 |
| Pb-18 | Gestión de lista blanca | Como administrador de seguridad, quiero consultar, agregar y quitar direcciones de la lista blanca, para adaptar las excepciones a mi red sin tocar la configuración del servidor. | Media | RF-06 |

### 3.5 M4. Correlación y persistencia

| ID | Nombre corto | Historia | Prioridad | RF |
|---|---|---|---|---|
| Pb-1 | Inicio de sesión | Como administrador de seguridad, quiero autenticarme para acceder a la API, al panel y a la app, para que solo personal autorizado vea incidentes o modifique bloqueos. | Alta | RF-08, RNF-04 |
| Pb-5 | Agrupación en incidentes | Como administrador de seguridad, quiero que los eventos de una misma IP y categoría se agrupen en un incidente, para ver un ataque como una unidad y no como cientos de líneas de log. | Alta | RF-07 |
| Pb-21 | Historial consultable | Como administrador de seguridad, quiero consultar el historial de incidentes filtrando por fecha, origen y severidad, para investigar lo ocurrido en un período. | Media | RF-08 |

### 3.6 M5. IA local

| ID | Nombre corto | Historia | Prioridad | RF |
|---|---|---|---|---|
| Pb-7 | Informe desde plantilla | Como administrador de seguridad, quiero que cada incidente tenga un informe en lenguaje natural (qué ocurrió, categoría OWASP, acción aplicada, recomendaciones) generado desde una plantilla, para entenderlo sin ser experto en seguridad y sin depender de la IA. | Alta | RF-10 |
| Pb-19 | Informe con IA local | Como administrador de seguridad, quiero que el informe del incidente lo redacte un modelo de lenguaje local, para obtener explicaciones más claras sin depender de la nube. | Media | RF-10 |
| Pb-20 | Clasificación local | Como administrador de seguridad, quiero que un modelo entrenado localmente clasifique cada petición sospechosa por tipo de ataque y severidad, para priorizar incidentes sin depender de la nube. | Media | RF-09 |

### 3.7 M6. Panel web

| ID | Nombre corto | Historia | Prioridad | RF |
|---|---|---|---|---|
| Pb-22 | Detalle de incidente | Como administrador de seguridad, quiero abrir un incidente y ver sus eventos y su informe, indicando si es "generado por IA" o "plantilla", para decidir qué hacer. | Media | RF-11 |
| Pb-23 | Liberar bloqueo desde el panel | Como administrador de seguridad, quiero liberar una IP bloqueada desde el panel web, para corregir un falso positivo sin usar la consola del servidor. | Media | RF-06, RF-12 |
| Pb-24 | Alertas en tiempo real | Como administrador de seguridad, quiero ver las alertas en el panel apenas ocurren, para reaccionar sin refrescar la página. | Media | RF-11 |
| Pb-25 | Estado de componentes | Como administrador de seguridad, quiero ver si nginx, Suricata, Fail2ban y Ollama están operativos, para saber cuándo la defensa está degradada. | Media | RF-11 |
| Pb-26 | Tablero de métricas | Como administrador de seguridad, quiero un tablero con incidentes por hora, bloqueos vigentes, tipos de ataque y top de IPs, para evaluar la situación de un vistazo. | Media | RF-11 |

### 3.8 M7. Móvil

| ID | Nombre corto | Historia | Prioridad | RF |
|---|---|---|---|---|
| Pb-8 | Conectar la app al servidor | Como administrador de seguridad, quiero configurar en la app la dirección del servidor e iniciar sesión, para consultar el sistema desde el celular. | Alta | RF-13 |
| Pb-9 | Registro del dispositivo | Como administrador de seguridad, quiero registrar mi dispositivo para recibir notificaciones, para que el servidor sepa a dónde enviar las alertas. | Alta | RF-13 |
| Pb-10 | Notificación de incidentes graves | Como administrador de seguridad, quiero recibir una notificación cuando un incidente sea de severidad alta o crítica, para enterarme aunque no esté frente al panel. | Alta | RF-13 |
| Pb-27 | Informe en el móvil | Como administrador de seguridad, quiero consultar el informe de un incidente desde la app, para evaluarlo en el momento. | Media | RF-13 |
| Pb-28 | Liberar bloqueo desde el móvil | Como administrador de seguridad, quiero liberar un bloqueo de forma remota desde la app, para corregir un falso positivo sin estar frente al equipo. | Media | RF-14 |

### 3.9 Épicas por resultado

| Épica | Historias de usuario |
|---|---|
| Detectar | Pb-2, Pb-3, Pb-4, Pb-11, Pb-12, Pb-13, Pb-14, Pb-29 |
| Responder | Pb-6, Pb-15, Pb-16, Pb-17, Pb-18 |
| Entender | Pb-5, Pb-7, Pb-19, Pb-20, Pb-21, Pb-22 |
| Operar | Pb-1, Pb-8, Pb-9, Pb-10, Pb-23, Pb-24, Pb-25, Pb-26, Pb-27, Pb-28 |

### 3.10 Criterios de aceptación ya identificados (para las tarjetas F4)

| HU | Criterio |
|---|---|
| Pb-2 | Cada detección genera un evento estructurado con fecha, IP, firma, categoría y URL |
| Pb-3 | Cero descartes en navegación legítima prolongada. Latencia añadida medida con k6, con y sin Suricata (RNF-02) |
| Pb-4 | Con Suricata detenido, la aplicación sigue respondiendo |
| Pb-5 | Una ráfaga de ataques de la misma IP y categoría produce un solo incidente sin saturar la ingesta |
| Pb-6 | Lista blanca por defecto (loopback, red de administración, gateway). Se banea la IP real del atacante, no la del proxy. El baneo queda asociado a su incidente. La acción se audita con usuario, fecha e IP afectada. Cero bloqueos en navegación legítima prolongada |
| Pb-7, Pb-19, Pb-20 | Funcionan sin conexión a internet (RNF-03) |
| Pb-19 | Tiempo máximo de 20 s; si se excede o la salida no tiene las secciones esperadas, se usa la plantilla. Se muestra la etiqueta "generado por IA" |
| Pb-20 | Bajo el umbral de confianza (propuesta 0,6) se devuelve `indeterminado` y prevalece la severidad de la firma |
| Pb-23, Pb-28 | La liberación se audita y la operación es idempotente |

---

## 4. Sprint Backlog (F5): Sprint 1 (candidato)

> **Nota de actualización:** el alcance de esta sección quedó como propuesta inicial (candidata) de Sprint 0. El alcance **oficial y vigente** del Sprint 1 es el definido en [Sprint1_Cimientos_y_Tarjetas_HU.md](Sprint1_Cimientos_y_Tarjetas_HU.md), que amplía las historias candidatas de Pb-1–Pb-7 a un total de **13 HU** (agrega Pb-8, Pb-9, Pb-10, Pb-20, Pb-27 y Pb-28 — móvil y clasificación local). Las tareas T-01 a T-55 de esta sección siguen sirviendo como referencia de cimientos/base técnica, pero para el detalle de HU, criterios de aceptación y tarjetas F4 del Sprint 1, ese documento es la fuente de verdad.

### 4.1 Datos del sprint

| Campo | Detalle |
|---|---|
| Objetivo del sprint (propuesta) | Demostrar de extremo a extremo, sobre la aplicación protegida, que un ataque de inyección SQL es detectado, descartado y agrupado en un incidente con su informe, y que un ataque sostenido termina con el origen bloqueado temporalmente en el firewall |
| Duración | **[POR DEFINIR]**. Regla del docente: de 2 a 4 semanas, igual para todos los sprints |
| Historias candidatas | Pb-1 a Pb-7 (propuesta inicial — **ampliado a 13 HU**, ver nota superior y [Sprint1_Cimientos_y_Tarjetas_HU.md](Sprint1_Cimientos_y_Tarjetas_HU.md)) |
| PHU y capacidad del equipo | Pendientes de Planning Poker |
| Tablero | Kanban con el Sprint Backlog únicamente (nunca el Product Backlog) |
| Herramienta de gestión | **[POR DEFINIR]** (Jira, Trello o Azure DevOps) |
| Cliente para la Revisión de Sprint | **[POR DEFINIR]** |

Todas las tareas parten en "Por hacer". Tipos: **Diseño**, **Implementación**, **Prueba** y **Técnica** (preparación de entorno o configuración). "Hab." indica una tarea habilitadora que no pertenece a una HU de usuario. La granularidad objetivo es de 2 a 3 días por tarea como máximo; el equipo la ajusta en el Planning.

### 4.2 Tareas por módulo

#### Transversal: entorno y base técnica (sin HU de usuario)

| ID | Tarea | HU | Tipo |
|---|---|---|---|
| T-01 | Aprovisionar la VM Ubuntu Server 24.04 LTS (2 vCPU, 4 GB de RAM, 25 GB) en red bridged o host-only, con IPv6 deshabilitado | Hab. | Técnica |
| T-02 | Escribir el script de aprovisionamiento versionado (Vagrant o script) que deje la VM reproducible con un solo comando | Hab. | Técnica |
| T-03 | Crear el repositorio en GitHub con `main` protegida, ramas `feature/<HU>`, commits convencionales y sin secretos | Hab. | Técnica |
| T-04 | Crear el esqueleto del servicio FastAPI con configuración (modo real o simulado, umbrales, rutas), formateo (ruff, black) y pytest | Hab. | Técnica |
| T-05 | Desplegar la aplicación protegida con Docker Compose, accesible solo por la red interna (propuesta: Juice Shop; decisión abierta #2) | Hab. | Técnica |
| T-06 | Implementar las interfaces `Fuente de eventos` y `Actuador de bloqueo` con sus versiones simuladas (`FakeSource`, `DryRunActuator`) para desarrollar sin la VM | Hab. | Técnica |

#### M1. Enrutamiento

Este sprint no incluye HU de M1 (Pb-15 y Pb-29 quedan para sprints posteriores). Sí incluye las tareas técnicas que la detección necesita.

| ID | Tarea | HU | Tipo |
|---|---|---|---|
| T-07 | Configurar nginx como proxy inverso (`proxy_pass`) hacia el destino interno, único punto de entrada público en HTTP (Modo A) | Hab. Pb-2 | Técnica |
| T-08 | Configurar `real_ip_header` y `set_real_ip_from` solo para proxies confiables y comprobar en el log la IP real del atacante | Hab. Pb-6 | Técnica |
| T-09 | Prueba: la aplicación no responde por fuera del proxy | Hab. Pb-2 | Prueba |

#### M2. Inspección y bloqueo en línea

| ID | Tarea | HU | Tipo |
|---|---|---|---|
| T-10 | Instalar Suricata (7.x u 8.x, repositorio oficial de OISF) en modo IDS y validar la configuración con `suricata -T` | Pb-2 | Técnica |
| T-11 | Descargar reglas con `suricata-update` (Emerging Threats Open), habilitar solo categorías web y dejarlas en caché para operar sin internet | Pb-2 | Técnica |
| T-12 | Configurar la salida `eve.json` con los campos del evento (fecha, IP, firma, categoría, URL) | Pb-2 | Implementación |
| T-13 | Escribir en `local.rules` la regla propia de inyección SQL para la aplicación de la demostración | Pb-2 | Implementación |
| T-14 | Prueba: un ataque con sqlmap contra el buscador genera alertas en `eve.json` con todos los campos | Pb-2 | Prueba |
| T-15 | Configurar nftables para enviar el tráfico a la cola de Suricata con la opción *bypass* (Modo A) | Pb-3, Pb-4 | Implementación |
| T-16 | Pasar Suricata a modo IPS (NFQUEUE) y definir en `drop.conf` solo las firmas de alta confianza | Pb-3 | Implementación |
| T-17 | Spike 1: una petición con un patrón de prueba se descarta y el tráfico normal pasa | Pb-3 | Prueba |
| T-18 | Evaluar la acción `reject` frente a `drop` para que el cliente reciba un cierre inmediato y no espere | Pb-3 | Diseño |
| T-19 | Prueba de falsos positivos: navegación legítima prolongada (navegador y k6) sin ningún descarte | Pb-3 | Prueba |
| T-20 | Medir con k6 la latencia añadida, con y sin Suricata (RNF-02) | Pb-3 | Prueba |
| T-21 | Spike 2: detener Suricata (`systemctl stop`) con tráfico en curso y comprobar que la aplicación sigue respondiendo | Pb-4 | Prueba |

#### M3. Respuesta por dirección

| ID | Tarea | HU | Tipo |
|---|---|---|---|
| T-22 | Diseñar el Motor de políticas: umbral (5 eventos de severidad media o mayor, misma IP, 60 s), duración inicial de 10 minutos y lista blanca | Pb-6 | Diseño |
| T-23 | Instalar Fail2ban y configurar la acción que crea y elimina las reglas de bloqueo en nftables (`bantime`, `ignoreip`) | Pb-6 | Técnica |
| T-24 | Implementar `Fail2banActuator` con `fail2ban-client set banip / unbanip`: IP validada con `ipaddress`, `subprocess` con lista de argumentos y operación idempotente | Pb-6 | Implementación |
| T-25 | Implementar el Motor de políticas que decide el bloqueo por umbral, por IP y ventana | Pb-6 | Implementación |
| T-26 | Implementar la lista blanca por defecto (loopback, red de administración, gateway); el actuador rechaza banear IPs en lista blanca | Pb-6 | Implementación |
| T-27 | Crear el usuario dedicado del servicio y un `sudoers` limitado a los comandos exactos de `fail2ban-client` | Pb-6 | Técnica |
| T-28 | Registrar el baneo asociado a su incidente y cada acción en la auditoría (usuario, fecha, IP afectada) | Pb-6 | Implementación |
| T-29 | Implementar el Conciliador mínimo: al arrancar contrasta los baneos de la base con Fail2ban y marca los vencidos como expirados | Pb-6 | Implementación |
| T-30 | Spike 3: un ataque simulado termina en una regla visible en `nft list ruleset` y en una fila de la base | Pb-6 | Prueba |
| T-31 | Prueba: una IP en lista blanca que ataca genera alerta sin baneo | Pb-6 | Prueba |
| T-32 | Prueba: el baneo se aplica a la IP real del atacante y no a la del proxy | Pb-6 | Prueba |
| T-33 | Prueba: el baneo vence a los 10 minutos y la regla desaparece del firewall | Pb-6 | Prueba |

#### M4. Correlación y persistencia

| ID | Tarea | HU | Tipo |
|---|---|---|---|
| T-34 | Diseñar el modelo de datos del sprint desde el diagrama de clases (Evento, Incidente, Baneo, ListaBlanca, Auditoria, Usuario), crear las tablas con SQLModel y configurar SQLite en modo WAL | Pb-1 (base para Pb-2, Pb-5, Pb-6) | Diseño |
| T-35 | Crear el usuario administrador único con contraseña con hash, sembrado desde una variable de entorno fuera del repositorio | Pb-1 | Implementación |
| T-36 | Implementar `POST /api/auth/login` con token de expiración de 8 h y límite de intentos de inicio de sesión | Pb-1 | Implementación |
| T-37 | Proteger las rutas de la API con verificación del token (401 sin token o con token vencido) | Pb-1 | Implementación |
| T-38 | Pruebas de inicio de sesión: credenciales válidas e inválidas, token vencido y límite de intentos | Pb-1 | Prueba |
| T-39 | Implementar `EveSource`: lectura continua de `eve.json` con `watchfiles`, detectando la rotación y reabriendo el archivo | Pb-2 | Implementación |
| T-40 | Interpretar las alertas y guardarlas como `Evento` (fecha en UTC, IP, firma, categoría, severidad, método, URL) | Pb-2 | Implementación |
| T-41 | Spike 4: el lector sobrevive a la rotación de `eve.json` (prueba con `logrotate`) | Pb-2 | Prueba |
| T-42 | Diseñar el Correlador: misma IP y misma categoría dentro de 5 minutos; ciclo abierto y cerrado | Pb-5 | Diseño |
| T-43 | Implementar el Correlador: crea o actualiza incidentes y asigna la severidad de la firma (1 alta, 2 media, 3 baja) | Pb-5 | Implementación |
| T-44 | Implementar el cierre de incidentes: sin baneo vigente y sin eventos nuevos en 5 minutos | Pb-5 | Implementación |
| T-45 | Exponer `GET /api/incidentes` y `GET /api/incidentes/{id}` autenticados, sin filtros (los filtros son Pb-21) | Pb-5 | Implementación |
| T-46 | Pruebas unitarias del Correlador con `FakeSource`: agrupación, ventana y cierre | Pb-5 | Prueba |
| T-47 | Prueba: una ráfaga de sqlmap produce un solo incidente por IP y categoría, sin saturar la ingesta (cola acotada y deduplicación) | Pb-5 | Prueba |

#### M5. IA local

Este sprint solo cubre el informe por plantilla (Pb-7). La IA local (Pb-19 y Pb-20) queda para un sprint posterior.

| ID | Tarea | HU | Tipo |
|---|---|---|---|
| T-48 | Diseñar la plantilla del informe (qué ocurrió, categoría OWASP, acción aplicada, recomendaciones) y la interfaz `Generador de informes`, para que Pb-19 se acople sin cambiar al llamador | Pb-7 | Diseño |
| T-49 | Definir la tabla configurable de tipo de ataque a categoría OWASP Top 10:2025 (inyección SQL a A05) | Pb-7 | Diseño |
| T-50 | Implementar el generador por plantilla y guardar el informe con `origen_informe = plantilla` | Pb-7 | Implementación |
| T-51 | Disparar la generación al crear el incidente, sin bloquear el hilo de lectura de eventos | Pb-7 | Implementación |
| T-52 | Prueba: cada incidente tiene un informe con las cuatro secciones, sin conexión a internet | Pb-7 | Prueba |

#### M6. Panel web y M7. Móvil

Sin tareas en este sprint. Pb-8, Pb-9 y Pb-10 (móvil) son las candidatas naturales del Sprint 2; antes debe cerrarse el spike 6 (el teléfono abre el panel por el punto de acceso del portátil). El panel completo (Pb-22 a Pb-26) queda después.

#### Cierre del sprint (transversal)

| ID | Tarea | HU | Tipo |
|---|---|---|---|
| T-53 | Ensayar la demostración de la Revisión de Sprint (ataque, descarte, incidente, baneo, informe) desde una VM recién aprovisionada | Hab. | Prueba |
| T-54 | Registrar las métricas del sprint: tasa de detección, falsos positivos, tiempo desde el primer evento hasta la regla de firewall y latencia añadida | Hab. | Prueba |
| T-55 | Actualizar los modelos incrementales (C4 nivel 2 y diagrama de clases) con lo aprendido en el sprint | Hab. | Diseño |

### 4.3 Vista por historia de usuario

| HU | Nombre corto | Tareas |
|---|---|---|
| Pb-1 | Inicio de sesión | T-34 a T-38 |
| Pb-2 | Detección de inyección SQL | T-07, T-09, T-10 a T-14, T-39 a T-41 |
| Pb-3 | Descarte de peticiones maliciosas | T-15 a T-20 |
| Pb-4 | Continuidad ante falla | T-15, T-21 |
| Pb-5 | Agrupación en incidentes | T-42 a T-47 |
| Pb-6 | Bloqueo temporal por umbral | T-08, T-22 a T-33 |
| Pb-7 | Informe desde plantilla | T-48 a T-52 |
| Transversales | Entorno y cierre | T-01 a T-06, T-53 a T-55 |

### 4.4 Definición de terminado (DoD, propuesta)

- Criterios de aceptación de la HU cumplidos.
- Código integrado en `main`.
- Pruebas pasando.
- Verificado en la VM con el ataque del guion.
- Sin secretos en el repositorio.
- Desplegable con un solo comando.

---

## 5. Trazabilidad de requisitos

| Requisito | Historias de usuario |
|---|---|
| RF-01 | Pb-29 (más la tarea técnica T-07) |
| RF-02 | Pb-15, Pb-6 (más la tarea técnica T-08) |
| RF-03 | Pb-2, Pb-3, Pb-11, Pb-12, Pb-13, Pb-14 |
| RF-04 | Pb-2 |
| RF-05 | Pb-6, Pb-16, Pb-17 |
| RF-06 | Pb-6, Pb-18, Pb-23 |
| RF-07 | Pb-5 |
| RF-08 | Pb-1, Pb-21 |
| RF-09 | Pb-20 |
| RF-10 | Pb-7, Pb-19 |
| RF-11 | Pb-22, Pb-24, Pb-25, Pb-26 |
| RF-12 | Pb-23 |
| RF-13 | Pb-8, Pb-9, Pb-10, Pb-27 |
| RF-14 | Pb-28 |
| RNF-01 | Pb-4 |
| RNF-02 | Criterio de aceptación de Pb-3 (tarea T-20) |
| RNF-03 | Criterio de aceptación de Pb-7, Pb-19 y Pb-20 |
| RNF-04 | Pb-1, Pb-6, Pb-23, Pb-28 (autenticación y auditoría) |

---

## 6. Pendientes

### 6.1 Resueltas (actualización del 20/09/2026)

| # | Pendiente | Resolución |
|---|---|---|
| 1 | Duración del sprint y forma de acreditar Scrum en este parcial | Confirmado con el docente: **2 semanas por sprint** |
| 3 | Herramienta de gestión y herramienta CASE | Gestión: **Jira**. CASE: **Enterprise Architect** (`docs/sw1.eap`) |
| 4 | Aplicación de la demostración | Confirmado: **Juice Shop v17.3.0**, ya desplegada (`infra/compose/app-protegida.yaml`) |
| 6 | RNF-02 (latencia) como criterio de Pb-3 y no como HU propia | Confirmado: quedó como criterio de aceptación de Pb-3 (ver tarjeta F4 en `Sprint1_Cimientos_y_Tarjetas_HU.md`), no como HU propia. El valor numérico del umbral sigue sin medir |

### 6.2 Siguen abiertas

| # | Pendiente | Propuesta por defecto |
|---|---|---|
| 2 | Product Owner, Scrum Master, desarrolladores y cliente clave | **[POR DEFINIR]** |
| 5 | PHU de cada HU y HU que entran al sprint | Planning Poker del equipo |
| 7 | Umbral aceptable de latencia añadida (RNF-02) y meta mínima del clasificador | Medir con k6 (`pruebas/guion.md`) antes de fijar el valor |
