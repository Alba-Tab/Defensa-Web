# Plataforma de Defensa Web en Tiempo de Ejecución
## Sprint 1: cimientos, objetivo e historias de usuario

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
| Fecha | 19 de septiembre de 2026 |

> **Estado del documento.** Los Puntos de Historia de Usuario (PHU) no se incluyen: los estima el equipo con Planning Poker, por eso figuran como **[POR ESTIMAR]**. Las prioridades son una propuesta hasta que las confirme el Product Owner. Los valores numéricos de las reglas (umbrales, duraciones) son iniciales y se calibran en las pruebas. La numeración de las HU es la del Product Backlog y no cambia.

---

## 1. Cimientos previos al Sprint 1 (lista estilo Sprint Backlog)

Tareas habilitadoras, sin HU de usuario, que dejan listas las bases de todo el software antes de desarrollar el Sprint 1: entorno, capa defensiva, esqueleto del backend, datos, IA, panel y móvil. Cada tarea tiene un criterio de terminado verificable el mismo día. Todas parten en "Por hacer". Tipos: **Gestión**, **Técnica**, **Diseño** y **Prueba**. La granularidad objetivo es de 2 a 3 días por tarea como máximo.

Cada instalación de la capa defensiva (C-14 a C-22) se agrega al script de aprovisionamiento (C-07), para que los 5 equipos tengan un entorno idéntico.

### 1.1 Gestión del proyecto y Scrum

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-01 | Definir el equipo Scrum: Product Owner, Scrum Master, desarrolladores y cliente clave para la Revisión de Sprint | Gestión | Los cuatro roles tienen nombre en el documento del proyecto |
| C-02 | Acordar con el docente la duración del sprint (2 a 4 semanas, igual para todos) y cómo se acredita Scrum en este parcial | Gestión | Duración y forma de acreditación registradas por escrito |
| C-03 | Elegir la herramienta de gestión (Jira, Trello o Azure DevOps) y crear el tablero Kanban con el Sprint Backlog únicamente | Gestión | Tablero con columnas Por hacer, En curso y Hecho; el Product Backlog no está en el tablero |
| C-04 | Elegir la herramienta CASE y crear el proyecto de modelos (UML 2.5+ y C4) | Gestión | Proyecto de modelos creado y accesible para todo el equipo |
| C-05 | Documentar el patrón de desarrollo: estándar de codificación (PEP 8 con ruff y black en Python; `dart format` y `flutter analyze` en Flutter), estrategia de ramas y flujo de integración | Diseño | Documento de una página aceptado por el equipo |

### 1.2 Transversal: entorno y repositorio

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-06 | Aprovisionar la VM Ubuntu Server 24.04 LTS (2 vCPU, 4 GB de RAM, 25 GB) en VirtualBox o Hyper-V, con red bridged o host-only (nunca NAT) e IPv6 deshabilitado | Técnica | La VM responde por SSH desde el anfitrión y su IP pertenece a la red del laboratorio |
| C-07 | Escribir el script de aprovisionamiento versionado (Vagrant o script) que instala y configura la capa defensiva | Técnica | Una VM nueva queda con la capa defensiva instalada con un solo comando, comprobado en otro equipo del grupo |
| C-08 | Crear el repositorio en GitHub con `main` protegida, ramas `feature/<HU>` con revisión, commits convencionales y `.gitignore` que excluya secretos | Técnica | Un push directo a `main` es rechazado y una búsqueda de secretos no encuentra ninguno |
| C-09 | Definir la estructura del repositorio por componente: servicio de defensa, app móvil, aprovisionamiento de la VM, IA (entrenamiento) y documentación | Diseño | Estructura creada, con un README por carpeta |
| C-10 | **Pospuesta** (aún no hay destino de despliegue). Reemplazo por ahora: formato al guardar, `pre-commit` (ruff y detección de secretos) y pytest local. La integración continua se reactiva cuando se defina el despliegue | Técnica | `pre-commit` bloquea un commit con error de formato o con un secreto |
| C-11 | Elegir la aplicación de la demostración con la prueba de 30 minutos sobre las finalistas (*propuesta*: Juice Shop) | Diseño | Decisión registrada con las cinco comprobaciones: responde por HTTP desde el portátil, tiene login, tiene un parámetro GET de búsqueda, consumo de RAM con `docker stats` y reinicio a estado limpio en menos de un minuto |
| C-12 | Desplegar la aplicación elegida con Docker Compose, accesible solo por la red interna de la VM | Técnica | Responde desde la VM, no responde por su puerto interno desde el anfitrión y se reinicia limpia en menos de un minuto. En desarrollo, `docker compose watch` refleja al guardar los cambios del código en el contenedor |
| C-13 | Instalar en el equipo anfitrión las herramientas de ataque simulado (sqlmap, Nikto, ffuf, OWASP ZAP) y Grafana k6 | Técnica | Un ataque de prueba con `curl` desde el anfitrión llega a la VM |

### 1.3 M1. Enrutamiento

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-14 | Instalar nginx como proxy inverso (`proxy_pass`) hacia la aplicación protegida, único punto de entrada público en HTTP (Modo A), con log de acceso | Técnica | La aplicación responde por el puerto público de la VM y no por su puerto interno desde el anfitrión |
| C-15 | Configurar `real_ip_header` y `set_real_ip_from` solo para proxies confiables | Técnica | Con `curl` desde el anfitrión, el log de acceso muestra la IP del anfitrión y no la del proxy |

### 1.4 M2. Inspección y bloqueo en línea

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-16 | Instalar Suricata (7.x u 8.x, repositorio oficial de OISF) en modo IDS | Técnica | `suricata -T` termina sin errores y el servicio queda activo |
| C-17 | Descargar reglas con `suricata-update` (Emerging Threats Open), habilitar solo categorías web y dejarlas en caché para operar sin internet | Técnica | Suricata arranca sin conexión a internet y su consumo de RAM cabe en los 4 GB de la VM (`free -m`) |
| C-18 | Configurar la salida `eve.json` (JSON por línea, con los campos de la alerta) y su rotación con `logrotate` | Técnica | Una alerta de prueba aparece en `eve.json` y la rotación está configurada |
| C-19 | Configurar nftables para enviar el tráfico HTTP a la cola de Suricata con la opción *bypass* (Modo A) | Técnica | `nft list ruleset` muestra la regla de cola con *bypass* y el tráfico normal pasa |

### 1.5 M3. Respuesta por dirección

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-20 | Instalar Fail2ban y configurar la acción que crea y elimina reglas de bloqueo en nftables (`bantime`, `findtime`, `maxretry`, `ignoreip`) | Técnica | `fail2ban-client set <jail> banip <IP>` crea una regla visible en `nft list ruleset`, evaluada antes de la cola de Suricata, y `unbanip` la elimina |
| C-21 | Crear el usuario dedicado del servicio de defensa y un `sudoers` limitado a los comandos exactos de `fail2ban-client` | Técnica | El usuario ejecuta `banip` y `unbanip` y ningún otro comando privilegiado |
| C-22 | Definir la lista blanca por defecto (loopback, red de administración, gateway) en `ignoreip` y en la configuración del servicio | Técnica | Los tres rangos figuran en ambos lugares y un intento de banear una IP de la lista es rechazado |

### 1.6 M4. Correlación y persistencia (base del backend)

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-23 | Crear el esqueleto del servicio FastAPI con la estructura de componentes del C4 nivel 3 (fuente de eventos, correlador, motor de políticas, actuador, clasificador, generador de informes, notificador, API, repositorio, conciliador, configuración) | Técnica | El servicio arranca en modo simulado y responde una ruta de prueba |
| C-24 | Implementar la configuración centralizada (modo real o simulado, umbrales, rutas) con secretos por variables de entorno | Técnica | Pasar de modo simulado a real solo requiere cambiar variables de entorno |
| C-25 | Implementar las interfaces `Fuente de eventos` y `Actuador de bloqueo` con sus versiones simuladas (`FakeSource`, `DryRunActuator`) | Técnica | El servicio corre completo en un equipo Windows sin la VM, con eventos simulados |
| C-26 | Diseñar el modelo de datos desde el diagrama de clases (Evento, Incidente, Baneo, ListaBlanca, Dispositivo, Auditoria, Usuario) y crear las tablas con SQLModel sobre SQLite en modo WAL (*propuesta*: Alembic para migrar el esquema entre sprints sin perder datos) | Diseño | Las tablas se crean desde el código y sus relaciones coinciden con el diagrama |
| C-27 | Implementar la capa Repositorio con transacciones cortas y fechas en UTC | Técnica | Una prueba de escrituras concurrentes termina sin bloqueos de base |
| C-28 | Configurar la base de pruebas: pytest, cliente de pruebas de FastAPI y fixtures con `FakeSource` y `DryRunActuator` | Prueba | `pytest` pasa con una prueba de humo del servicio |

### 1.7 M5. IA local (datos y entorno)

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-29 | Verificar la disponibilidad y la licencia del conjunto HTTP CSIC 2010 y descargarlo | Técnica | Conjunto descargado, o decisión documentada de otra fuente si no está disponible |
| C-30 | Definir el esquema de los datos etiquetados (campos de entrada y clases: benigno, sqli, xss, traversal, escaneo, fuerza_bruta, indeterminado) y el procedimiento para capturar tráfico propio etiquetado por herramienta de ataque y navegación legítima | Diseño | Esquema documentado y script de captura probado con una muestra |
| C-31 | Preparar el entorno de entrenamiento reproducible (Python, scikit-learn, joblib) con versiones fijadas | Técnica | Un script entrena un modelo trivial, lo exporta con joblib y el servicio lo carga |
| C-32 | Instalar Ollama en el equipo anfitrión y descargar un modelo pequeño (de 1 a 3 B de parámetros). No bloquea el Sprint 1: informa a Pb-19 | Técnica | La VM consulta el modelo por la red host-only |

### 1.8 M6. Panel web (base)

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-33 | Crear el esqueleto del panel servido por el mismo servicio: plantilla base con Jinja2 y HTMX, Alpine.js y Chart.js servidos desde archivos locales, sin CDN. No bloquea el Sprint 1: el panel es del Sprint 2 | Técnica | La página base se muestra sin conexión a internet |

### 1.9 M7. Móvil (base)

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-34 | Instalar el entorno de Flutter (Dart) y el SDK de Android en los equipos Windows y crear el proyecto de la app | Técnica | La app de ejemplo compila y corre en un teléfono Android real |
| C-35 | Definir la arquitectura y el stack de la app (*propuesta*: `flutter_riverpod`, `dio` con interceptor del token, `go_router`, `flutter_secure_storage`) y crear el esqueleto con navegación entre pantallas vacías (inicio de sesión, incidentes, detalle, bloqueos, configuración) | Diseño | El esqueleto navega entre las cinco pantallas y `flutter analyze` no reporta errores |
| C-36 | Permitir HTTP plano en Android para el laboratorio (`usesCleartextTraffic` o `network_security_config` limitada a la IP del laboratorio) | Técnica | La app hace una petición HTTP a la VM y recibe respuesta |
| C-37 | Crear el proyecto de Firebase con Cloud Messaging, generar la cuenta de servicio y guardar la clave JSON fuera del repositorio, con su ruta en una variable de entorno; conectar la app al proyecto | Técnica | El proyecto existe y una búsqueda de secretos no encuentra la clave en el repositorio |
| C-38 | Habilitar la salida a internet del servicio de defensa para llamar a FCM: red bridged con salida a internet, o un segundo adaptador NAT solo para esa salida; y el punto de acceso del portátil compartiendo conexión con el teléfono | Técnica | Desde la VM, una petición HTTPS a Google responde y el tráfico de ataque sigue entrando por la interfaz bridged o host-only |

### 1.10 Verificaciones técnicas (spikes)

Son prototipos descartables: sirven para comprobar la viabilidad antes de construir, no tienen calidad de producción.

| ID | Spike | Tipo | Criterio de éxito |
|---|---|---|---|
| C-39 | Spike 1. Cola de Suricata (Modo A) | Prueba | Una petición con un patrón de prueba se descarta y el tráfico normal pasa. El Modo B (TLS en nginx) queda para Pb-29 |
| C-40 | Spike 2. Fail-open | Prueba | Con `systemctl stop suricata` y tráfico en curso, la aplicación sigue respondiendo |
| C-41 | Spike 3. Baneo de extremo a extremo | Prueba | Un ataque simulado termina en una regla visible en `nft list ruleset` y en una fila de la base |
| C-42 | Spike 4. Lector de eventos | Prueba | Un lector con `watchfiles` sobrevive a la rotación de `eve.json` (prueba con `logrotate`) |
| C-43 | Spike 5. IA para la ficha. No bloquea el Sprint 1: informa a Pb-19 | Prueba | La ficha se genera en menos de 20 s en la máquina de la demostración, o se decide un modelo más pequeño |
| C-44 | Spike 6. Alcance móvil | Prueba | El navegador del teléfono alcanza el servidor por el punto de acceso del portátil |
| C-45 | Spike 7. Push con FCM | Prueba | El backend envía una notificación con `firebase-admin` y llega a un teléfono Android real con la app cerrada; al tocarla se abre una pantalla de detalle |

### 1.11 Modelos iniciales y cierre

| ID | Tarea | Tipo | Criterio de terminado |
|---|---|---|---|
| C-46 | Esbozar el modelo de contexto: C4 nivel 1 con leyenda y relaciones nombradas con verbo y protocolo | Diseño | Diagrama creado con la herramienta CASE |
| C-47 | Esbozar el modelo de arquitectura: C4 nivel 2 (contenedores) y nivel 3 (componentes del servicio de defensa) | Diseño | Ambos diagramas creados, sin mezclar niveles |
| C-48 | Esbozar el modelo de datos: diagrama de clases UML | Diseño | Diagrama coherente con las tablas de C-26 |
| C-49 | Documentar la definición de terminado (DoD), el plan de pruebas (ataque simulado y señal esperada) y el guion de ataque de la demostración | Diseño | Documento aceptado por el equipo y por el Product Owner |
| C-50 | Sprint Planning: estimar los PHU de las 13 HU con Planning Poker, confirmar las prioridades con el Product Owner y comprometer el Sprint Backlog | Gestión | PHU registrados en cada tarjeta y HU confirmadas |

### 1.12 Definición de listo para iniciar el Sprint 1

El Sprint 1 arranca cuando se cumple todo lo siguiente:

- Roles, duración del sprint y herramientas definidos (C-01 a C-05).
- VM reproducible, repositorio con estructura y verificaciones locales (`pre-commit`), aplicación protegida y herramientas de ataque operativas (C-06 a C-13, sin C-10, que quedó pospuesta).
- Capa defensiva instalada y probada: nginx, Suricata, nftables y Fail2ban (C-14 a C-22).
- Backend base corriendo en modo simulado, con el modelo de datos creado (C-23 a C-28).
- Entorno y datos de la IA preparados (C-29 a C-31).
- App móvil base que compila, alcanza el servidor y tiene Firebase configurado (C-34 a C-38).
- Spikes 1, 2, 3, 4, 6 y 7 superados (C-39 a C-42, C-44 y C-45).
- Modelos iniciales, DoD, plan de pruebas y guion de ataque documentados (C-46 a C-49).
- PHU estimados y HU confirmadas por el Product Owner (C-50).

No bloquean el arranque: C-32 (Ollama), C-33 (esqueleto del panel) y C-43 (spike 5), porque corresponden a historias del Sprint 2.

---

## 2. Historias de usuario del Sprint 1

13 de las 29 historias del Product Backlog. Se listan en orden lógico de funcionamiento: cada HU depende solo de las anteriores de esta lista.

| Orden | ID | Nombre corto | Prioridad | Módulo | Depende de | PHU |
|---|---|---|---|---|---|---|
| 1 | Pb-1 | Inicio de sesión | Alta | M4 | Cimientos | **[POR ESTIMAR]** |
| 2 | Pb-2 | Detección de inyección SQL | Alta | M2 | Cimientos | **[POR ESTIMAR]** |
| 3 | Pb-3 | Descarte de peticiones maliciosas | Alta | M2 | Pb-2 | **[POR ESTIMAR]** |
| 4 | Pb-4 | Continuidad ante falla | Alta | M2 | Pb-3 | **[POR ESTIMAR]** |
| 5 | Pb-5 | Agrupación en incidentes | Alta | M4 | Pb-1, Pb-2 | **[POR ESTIMAR]** |
| 6 | Pb-6 | Bloqueo temporal por umbral | Alta | M3 | Pb-5 | **[POR ESTIMAR]** |
| 7 | Pb-7 | Informe desde plantilla | Alta | M5 | Pb-5, Pb-6 | **[POR ESTIMAR]** |
| 8 | Pb-20 | Clasificación local | Alta (propuesta) | M5 | Pb-2, Pb-5 | **[POR ESTIMAR]** |
| 9 | Pb-8 | Conectar la app al servidor | Alta | M7 | Pb-1 | **[POR ESTIMAR]** |
| 10 | Pb-9 | Registro del dispositivo | Alta | M7 | Pb-8 | **[POR ESTIMAR]** |
| 11 | Pb-10 | Notificación de incidentes graves | Alta | M7 | Pb-5, Pb-9 (y Pb-20 para la severidad) | **[POR ESTIMAR]** |
| 12 | Pb-27 | Informe en el móvil | Alta (propuesta) | M7 | Pb-7, Pb-8 | **[POR ESTIMAR]** |
| 13 | Pb-28 | Liberar bloqueo desde el móvil | Alta (propuesta) | M7 | Pb-6, Pb-8 | **[POR ESTIMAR]** |
| | | **Total de PHU** | | | | **[POR ESTIMAR]** |

Pb-20, Pb-27 y Pb-28 figuran como Media en el Product Backlog. Se proponen como Alta porque, sin ellas, el ciclo no se cierra (la notificación no lleva a ningún lado y un bloqueo automático no se puede deshacer) o no se cumple la IA local entrenada que exige el parcial. Lo confirma el Product Owner.

Pb-1 y Pb-8 no dependen de la detección: el equipo puede construirlas en paralelo con Pb-2 a Pb-7.

---

## 3. Objetivo del Sprint 1

> Entregar un MVP operativo de defensa para la aplicación protegida: detectar y descartar ataques de inyección SQL, bloquear temporalmente al origen que insiste, explicar cada incidente con informe y clasificación local, y permitir al administrador recibir la alerta y liberar el bloqueo desde el celular, sin comprometer la disponibilidad si el motor de inspección falla.

### 3.1 Qué queda operativo al final del sprint

1. Un atacante lanza inyección SQL contra la aplicación protegida.
2. La petición se descarta antes de llegar a la aplicación y queda un evento estructurado.
3. Los eventos se agrupan en un incidente, que el clasificador local etiqueta con tipo de ataque, confianza y severidad.
4. Si el ataque es sostenido (5 eventos en 60 s), la IP se bloquea 10 minutos en el firewall.
5. El incidente tiene un informe desde plantilla y, si es de severidad alta, llega una notificación al móvil.
6. El administrador abre el informe en la app, ve los bloqueos vigentes y libera el bloqueo. La acción queda auditada.
7. Si Suricata se detiene, la aplicación sigue respondiendo.

### 3.2 Fuera del incremento

| HU | Qué queda fuera | Motivo |
|---|---|---|
| Pb-11 a Pb-14 | XSS, path traversal, escaneo y sondeo de archivos | Aditivas sobre la misma tubería de Pb-2 |
| Pb-15, Pb-16, Pb-18 | Límite de tasa, bloqueo progresivo, gestión de lista blanca | Refinan algo que ya funciona. Sin Pb-16 no existe la severidad crítica |
| Pb-17 | Bloqueo por fuerza bruta | Decisión de diseño pendiente sobre cómo registrar en la base los baneos hechos por Fail2ban |
| Pb-19 | Informe con IA local (Ollama) | Mejora de Pb-7; depende del spike 5. Planificada para el Sprint 2 — no es condición para cumplir el requisito técnico 1, que ya satisface el clasificador local (Pb-20), confirmado con el docente |
| Pb-21 a Pb-26 | Historial con filtros y panel web | El móvil es el único canal del MVP |
| Pb-29 | Terminación TLS | El MVP inspecciona HTTP en claro (Modo A). Se declara como limitación |

---

## 4. Detalle de las historias de usuario (tarjetas F4)

Todas las tarjetas tienen los mismos campos: identificador, nombre corto, prioridad, PHU, Como / Quiero / Para, criterios de aceptación y conversación (opcional). La conversación describe qué se debe hacer y las reglas de negocio, no cómo lo resuelve el diseño.

### Pb-1. Inicio de sesión

| Campo | Detalle |
|---|---|
| Identificador | Pb-1 |
| Nombre corto | Inicio de sesión |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M4 · RF-08, RNF-04 |
| Depende de | Cimientos (C-23 a C-28) |
| Como | administrador de seguridad |
| Quiero | autenticarme en el sistema (API, panel y app) |
| Para | que solo personal autorizado vea incidentes o modifique bloqueos |

**Criterios de aceptación**

1. Con credenciales válidas, `POST /api/auth/login` devuelve un token con expiración de 8 horas.
2. Con credenciales inválidas responde 401 con un mensaje único, sin indicar si falló el usuario o la contraseña.
3. Toda ruta de la API, salvo el inicio de sesión, responde 401 sin token, con token vencido o con token alterado.
4. La contraseña se guarda solo con hash; el usuario administrador se crea desde una variable de entorno y ningún secreto figura en el repositorio.
5. Tras 5 intentos fallidos desde una misma IP en 60 s, los siguientes se rechazan con 429 durante un período definido (propuesta: 5 minutos).

**Conversación (opcional)**

- Existe un único usuario administrador (decisión abierta #5). No hay registro de usuarios ni recuperación de contraseña en el MVP.
- La misma autenticación sirve a la API, al panel y a la app.
- Un token vencido obliga a iniciar sesión de nuevo; no hay renovación automática en el MVP.

---

### Pb-2. Detección de inyección SQL

| Campo | Detalle |
|---|---|
| Identificador | Pb-2 |
| Nombre corto | Detección de inyección SQL |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M2 · RF-03, RF-04 |
| Depende de | Cimientos (C-14 a C-19, C-26, C-27, C-42) |
| Como | administrador de seguridad |
| Quiero | que las peticiones con patrones de inyección SQL se detecten y queden registradas como eventos estructurados |
| Para | identificar el ataque cuando ocurre y poder auditarlo |

**Criterios de aceptación**

1. Un ataque con sqlmap contra el parámetro de búsqueda de la aplicación protegida genera alertas en `eve.json`.
2. Cada alerta incluye fecha, IP de origen, identificador y nombre de la firma, categoría, severidad de la firma, método y URL.
3. El servicio lee las alertas y las guarda como eventos en la base, con la fecha en UTC.
4. La IP de origen registrada es la del equipo atacante, no la del proxy.
5. Si `eve.json` rota, el servicio sigue leyendo sin perder eventos (prueba con `logrotate`).
6. La detección funciona sin conexión a internet, con las reglas en caché.
7. La navegación legítima de prueba no genera alertas de inyección SQL.

**Conversación (opcional)**

- El alcance del MVP es la inyección SQL. Los demás tipos de ataque (Pb-11 a Pb-14) se suman después sobre la misma tubería.
- Se empieza en modo detección (solo alerta); el descarte se activa en Pb-3.
- Se combinan las firmas de Emerging Threats Open (solo categorías web) con una regla propia para la aplicación de la demostración.

---

### Pb-3. Descarte de peticiones maliciosas

| Campo | Detalle |
|---|---|
| Identificador | Pb-3 |
| Nombre corto | Descarte de peticiones maliciosas |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M2 · RF-03 (y RNF-02 como criterio) |
| Depende de | Pb-2; spike 1 (C-39) |
| Como | administrador de seguridad |
| Quiero | que las peticiones que coincidan con firmas de alta confianza se descarten antes de llegar a la aplicación |
| Para | evitar el daño y no solo registrarlo |

**Criterios de aceptación**

1. Una petición que coincide con una firma de alta confianza configurada para descarte no llega a la aplicación protegida (no aparece en su log) y queda registrada como evento con acción de descarte.
2. Solo se descartan las firmas de alta confianza definidas; las demás solo generan alerta.
3. Cero descartes durante una sesión prolongada de navegación legítima con navegador y k6 (propuesta: 10 minutos).
4. La latencia añadida por la inspección se mide con k6, con y sin Suricata, y se registra. El umbral aceptable lo define el Product Owner **[POR DEFINIR]** (RNF-02).
5. Se documenta lo que experimenta el cliente ante un descarte (`drop` frente a `reject`) y se elige la acción que evita que espere sin respuesta.

**Conversación (opcional)**

- Una regla mal afinada descarta tráfico legítimo. Por eso son pocas las firmas en descarte y solo se activan después de probar con navegación normal.
- La demostración debe explicar qué ve el cliente cuya petición fue descartada.

---

### Pb-4. Continuidad ante falla

| Campo | Detalle |
|---|---|
| Identificador | Pb-4 |
| Nombre corto | Continuidad ante falla |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M2 · RNF-01 |
| Depende de | Pb-3; spike 2 (C-40) |
| Como | cliente legítimo |
| Quiero | seguir accediendo a la aplicación aunque el motor de inspección se detenga |
| Para | que la defensa nunca sea la causa de una caída |

**Criterios de aceptación**

1. Con Suricata detenido y tráfico en curso, una petición legítima a la aplicación protegida sigue recibiendo respuesta correcta.
2. Al volver a iniciar Suricata, la inspección se reanuda sin reconfigurar: una petición maliciosa de prueba vuelve a descartarse.
3. Mientras el motor está detenido, `GET /api/salud` (autenticado) lo informa como degradado.
4. No se requiere intervención manual sobre nginx ni sobre la aplicación para recuperar el servicio.

**Conversación (opcional)**

- Decisión de negocio: la disponibilidad prevalece sobre la protección (fail-open). Mientras dura la caída no hay inspección.
- El criterio 3 evita que la defensa falle en silencio. El panel mostrará el mismo estado en Pb-25 (Sprint 2).

---

### Pb-5. Agrupación en incidentes

| Campo | Detalle |
|---|---|
| Identificador | Pb-5 |
| Nombre corto | Agrupación en incidentes |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M4 · RF-07 |
| Depende de | Pb-1, Pb-2 |
| Como | administrador de seguridad |
| Quiero | que los eventos de una misma IP y categoría se agrupen en un incidente |
| Para | ver un ataque como una unidad y no como cientos de líneas de log |

**Criterios de aceptación**

1. Los eventos de la misma IP y la misma categoría dentro de una ventana de 5 minutos se agrupan en un único incidente `abierto`.
2. Un evento de otra IP o de otra categoría crea un incidente distinto.
3. El incidente registra IP de origen, tipo de ataque, severidad, inicio y última actividad. **La severidad del incidente usa una escala invertida respecto a la de la firma** (`evento.severidad_firma`: 1 alta, 2 media, 3 baja): `incidente.severidad` va de 1 (baja) a 3 (alta) en este sprint — 4 (crítica) queda para Pb-16. El correlador convierte al ingresar el evento: firma 1→3, firma 2→2, firma 3→1. Ver `Modelo_datos.md` (fuente de verdad del esquema) para el detalle de la conversión.
4. Una ráfaga de sqlmap con cientos de eventos produce un solo incidente por IP y categoría, sin saturar la ingesta.
5. Un incidente pasa a `cerrado` cuando no tiene baneo vigente y no recibe eventos nuevos durante 5 minutos.
6. `GET /api/incidentes` y `GET /api/incidentes/{id}` (autenticados) devuelven los incidentes y sus eventos; sin token responden 401.

**Conversación (opcional)**

- Un evento que llega después del cierre abre un incidente nuevo.
- La severidad final combina la de la firma y la del clasificador (Pb-20). Los filtros del historial son Pb-21.
- Agrupar nunca debe frenar la lectura de eventos.

---

### Pb-6. Bloqueo temporal por umbral

| Campo | Detalle |
|---|---|
| Identificador | Pb-6 |
| Nombre corto | Bloqueo temporal por umbral |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M3 · RF-05, RF-02, RF-06, RNF-04 |
| Depende de | Pb-5; cimientos (C-20 a C-22); spike 3 (C-41) |
| Como | administrador de seguridad |
| Quiero | que una IP que supere el umbral de eventos en una ventana de tiempo se bloquee temporalmente en el firewall |
| Para | cortar un ataque sostenido sin intervención manual |

**Criterios de aceptación**

1. Una IP que genera 5 eventos de severidad media o mayor en 60 s queda bloqueada: su regla es visible en `nft list ruleset` y el baneo consta en la base como `vigente`.
2. El bloqueo dura 10 minutos; al vencer, la regla desaparece del firewall y el baneo pasa a `expirado`.
3. Se bloquea la IP real del atacante, no la del proxy.
4. Nunca se bloquea loopback, la red de administración ni el gateway: una IP de la lista blanca que ataca genera alerta sin baneo.
5. El baneo queda asociado al incidente que lo originó.
6. Cada bloqueo se audita con usuario (o "sistema" si lo decide la política), fecha e IP afectada.
7. Si el firewall no aplica el bloqueo, el baneo queda `fallido` y se reintenta. Al reiniciar el servicio, los baneos de la base se contrastan con el estado real del firewall y los vencidos se marcan `expirado`.
8. Un valor con formato de IP inválido se rechaza y no ejecuta ningún comando en el servidor.
9. Cero bloqueos durante una sesión prolongada de navegación legítima (propuesta: 10 minutos con navegador y k6).
10. Se mide y registra el tiempo desde el primer evento hasta la regla en el firewall.

**Conversación (opcional)**

- El umbral (5 eventos en 60 s) y la duración (10 minutos) son valores iniciales que se calibran en las pruebas.
- Solo el motor de políticas decide bloquear. La IA nunca lo hace.
- Fuera de esta HU: la duración progresiva ante reincidencia (Pb-16), el bloqueo por fuerza bruta (Pb-17) y la gestión de la lista blanca (Pb-18).
- Con usuarios tras una misma IP (CGNAT) puede haber bloqueos de inocentes. Por eso el bloqueo es corto y se puede liberar rápido (Pb-28).

---

### Pb-7. Informe desde plantilla

| Campo | Detalle |
|---|---|
| Identificador | Pb-7 |
| Nombre corto | Informe desde plantilla |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M5 · RF-10 (y RNF-03 como criterio) |
| Depende de | Pb-5, Pb-6 |
| Como | administrador de seguridad |
| Quiero | que cada incidente tenga un informe en lenguaje natural generado desde una plantilla |
| Para | entenderlo sin ser experto en seguridad y sin depender de la IA |

**Criterios de aceptación**

1. Cada incidente tiene un informe con cuatro secciones: qué ocurrió, categoría OWASP, acción aplicada y recomendaciones.
2. La categoría OWASP Top 10:2025 se asigna según el tipo de ataque (inyección SQL corresponde a A05).
3. La sección "acción aplicada" refleja lo ocurrido (solo alerta, petición descartada o IP bloqueada por un tiempo) y se actualiza cuando se aplica un bloqueo o se cierra el incidente.
4. El informe se guarda con origen `plantilla` y se devuelve en `GET /api/incidentes/{id}`.
5. Se genera sin conexión a internet y sin frenar la lectura de eventos.
6. Los datos capturados de la petición (URL, parámetros) aparecen truncados y como texto plano; nunca se interpretan como instrucciones ni como código.

**Conversación (opcional)**

- Este informe es la base: todo incidente tiene siempre una ficha. Pb-19 (redacción con IA local) la mejorará después y usará esta plantilla como respaldo.
- Las recomendaciones son un texto fijo por categoría. Para inyección SQL, por ejemplo: consultas parametrizadas y validación de entradas.

---

### Pb-20. Clasificación local

| Campo | Detalle |
|---|---|
| Identificador | Pb-20 |
| Nombre corto | Clasificación local |
| Prioridad | Alta (propuesta; en el backlog figura como Media) |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M5 · RF-09 (y RNF-03 como criterio) |
| Depende de | Pb-2, Pb-5; cimientos de IA (C-29 a C-31) |
| Como | administrador de seguridad |
| Quiero | que un modelo entrenado localmente clasifique cada petición sospechosa por tipo de ataque y severidad |
| Para | priorizar incidentes sin depender de la nube |

**Criterios de aceptación**

1. Existe un modelo entrenado localmente (scikit-learn, exportado con joblib) que el servicio carga y usa sin conexión a internet.
2. El modelo recibe método, URI decodificada, parámetros, fragmento del cuerpo, user-agent y categoría de la firma, y devuelve una clase de {benigno, sqli, xss, traversal, escaneo, fuerza_bruta, indeterminado} con su confianza.
3. Con confianza inferior al umbral (propuesta: 0,6) devuelve `indeterminado` y prevalece la severidad de la firma.
4. La severidad del incidente es la mayor entre la de la firma y la del clasificador.
5. La evaluación, con partición de entrenamiento y prueba, reporta precisión, exhaustividad y matriz de confusión por clase. La meta mínima para `sqli` la fija el equipo tras la primera evaluación **[POR DEFINIR]**.
6. Los datos de entrenamiento (HTTP CSIC 2010, tráfico propio etiquetado por herramienta de ataque y navegación legítima) y su licencia quedan documentados, y un solo comando regenera el modelo.
7. La clasificación se hace en segundo plano: nunca frena la lectura de eventos ni decide bloquear.

**Conversación (opcional)**

- Es el modelo "entrenado de forma personalizada" que exige el parcial. Falta confirmar con el docente si el clasificador basta o si también debe contar el modelo de lenguaje (Pb-19).
- Si no hay datos suficientes de una clase, se reporta y esa clase se mantiene como `indeterminado`.
- La severidad crítica (alta más reincidente) necesita Pb-16. En este sprint solo existen alta, media y baja.
- Es la HU con más incertidumbre: dataset, entrenamiento y evaluación.

---

### Pb-8. Conectar la app al servidor

| Campo | Detalle |
|---|---|
| Identificador | Pb-8 |
| Nombre corto | Conectar la app al servidor |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M7 · RF-13 |
| Depende de | Pb-1; cimientos móviles (C-34 a C-36); spike 6 (C-44) |
| Como | administrador de seguridad |
| Quiero | configurar en la app la dirección del servidor e iniciar sesión |
| Para | consultar el sistema desde el celular |

**Criterios de aceptación**

1. La app permite escribir y guardar la dirección (IP y puerto) del servidor; el valor persiste al cerrar la app.
2. Con credenciales válidas, la app inicia sesión y guarda el token en el almacenamiento seguro del dispositivo.
3. Con credenciales inválidas o con el servidor inalcanzable, muestra un mensaje claro y no se cierra.
4. Si el servidor responde 401 por token vencido, la app vuelve a la pantalla de inicio de sesión.
5. En Android, la app se comunica por HTTP plano con el servidor del laboratorio.
6. El teléfono alcanza el servidor a través del punto de acceso del portátil.

**Conversación (opcional)**

- La demostración móvil es en Android (decisión abierta #10). Flutter mantiene un solo código para Android e iOS, pero compilar para iOS exige Mac y una cuenta de Apple Developer.
- La dirección del servidor es editable porque cambia entre redes (aula, casa, punto de acceso).

---

### Pb-9. Registro del dispositivo

| Campo | Detalle |
|---|---|
| Identificador | Pb-9 |
| Nombre corto | Registro del dispositivo |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M7 · RF-13 |
| Depende de | Pb-8; cimientos de push (C-37, C-38) |
| Como | administrador de seguridad |
| Quiero | registrar mi dispositivo para recibir notificaciones |
| Para | que el servidor sepa a dónde enviar las alertas |

**Criterios de aceptación**

1. La app solicita el permiso de notificaciones y obtiene el token de FCM del dispositivo.
2. La app envía el token a `POST /api/dispositivos` (autenticado); el servidor guarda token, plataforma, fecha de alta y fecha de actualización.
3. Registrar el mismo dispositivo dos veces no crea duplicados.
4. Si FCM cambia el token, la app lo actualiza en el servidor sin intervención del usuario.
5. Si el usuario rechaza el permiso, la app avisa que no recibirá alertas y sigue funcionando.
6. Si FCM informa que un token ya no es válido (`UNREGISTERED`), el servidor elimina ese dispositivo.

**Conversación (opcional)**

- FCM requiere internet tanto en el teléfono como en el servidor (cimiento C-38).
- Un administrador puede tener varios dispositivos registrados.

---

### Pb-10. Notificación de incidentes graves

| Campo | Detalle |
|---|---|
| Identificador | Pb-10 |
| Nombre corto | Notificación de incidentes graves |
| Prioridad | Alta |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M7 · RF-13 |
| Depende de | Pb-5, Pb-9 (y Pb-20 para la severidad); spike 7 (C-45) |
| Como | administrador de seguridad |
| Quiero | recibir una notificación cuando un incidente sea de severidad alta o crítica |
| Para | enterarme aunque no esté frente al panel |

**Criterios de aceptación**

1. Al abrirse un incidente de severidad alta, el servidor envía una notificación push a todos los dispositivos registrados.
2. Los incidentes de severidad media o baja no generan notificación.
3. Se envía una sola notificación por incidente al abrirse y una segunda solo si el incidente escala a alta; los eventos posteriores no generan más avisos.
4. La notificación llega a un teléfono Android real con la app cerrada y, al tocarla, se abre el detalle de ese incidente.
5. Si no hay internet, la app abierta recibe la alerta por `GET /api/eventos` (SSE).
6. La notificación incluye tipo de ataque, severidad e IP, y no incluye el contenido capturado de la petición.
7. Si un dispositivo resulta inválido, se elimina y el envío continúa con los demás.

**Conversación (opcional)**

- La severidad crítica (alta más reincidente) necesita Pb-16. En este sprint solo notifican los incidentes de severidad alta.
- Sin internet no hay push. El respaldo por SSE cubre solo la app abierta.

---

### Pb-27. Informe en el móvil

| Campo | Detalle |
|---|---|
| Identificador | Pb-27 |
| Nombre corto | Informe en el móvil |
| Prioridad | Alta (propuesta; en el backlog figura como Media) |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M7 · RF-13 |
| Depende de | Pb-7, Pb-8 |
| Como | administrador de seguridad |
| Quiero | consultar el informe de un incidente desde la app |
| Para | evaluarlo en el momento |

**Criterios de aceptación**

1. La app muestra la lista de incidentes, con el más reciente primero, con IP de origen, tipo de ataque, severidad y estado.
2. Al abrir un incidente se muestra su informe con las cuatro secciones y su origen (`plantilla`).
3. Al tocar una notificación, la app abre el detalle del incidente correspondiente.
4. Los datos capturados de la petición se muestran como texto plano.
5. Sin sesión válida, la app pide iniciar sesión antes de mostrar cualquier dato.
6. Si el incidente todavía no tiene informe, la app lo indica sin fallar.

**Conversación (opcional)**

- La lista de incidentes forma parte de esta HU porque sin ella la notificación no tiene a dónde llevar. El filtrado por fecha, origen y severidad es Pb-21.
- Cuando exista Pb-19, la app mostrará la etiqueta "generado por IA" o "plantilla".

---

### Pb-28. Liberar bloqueo desde el móvil

| Campo | Detalle |
|---|---|
| Identificador | Pb-28 |
| Nombre corto | Liberar bloqueo desde el móvil |
| Prioridad | Alta (propuesta; en el backlog figura como Media) |
| PHU (Planning Poker) | **[POR ESTIMAR]** |
| Módulo y requisitos | M7 · RF-14, RNF-04 |
| Depende de | Pb-6, Pb-8 |
| Como | administrador de seguridad |
| Quiero | liberar un bloqueo de forma remota desde la app |
| Para | corregir un falso positivo sin estar frente al equipo |

**Criterios de aceptación**

1. La app lista los bloqueos vigentes con IP, incidente asociado y hora de expiración (`GET /api/baneos`).
2. Al confirmar la liberación, la regla desaparece de `nft list ruleset` y el baneo pasa a `liberado`.
3. Liberar una IP que ya no está bloqueada no produce error.
4. La liberación se audita con usuario, fecha e IP afectada.
5. La app pide confirmación explícita antes de liberar.
6. `POST /api/baneos/{ip}/liberar` responde 401 sin token y rechaza un valor con formato de IP inválido sin ejecutar ningún comando.
7. Tras liberar, una petición legítima desde esa IP vuelve a llegar a la aplicación.

**Conversación (opcional)**

- Es la forma de deshacer un bloqueo automático, en especial con usuarios tras una misma IP (CGNAT).
- Propuesta: pedir la biometría del dispositivo antes de liberar (`local_auth`). No es obligatoria para el MVP.
- La liberación desde el panel web es Pb-23 (Sprint 2).

---

## 5. Pendientes

### 5.1 Resueltas (actualización del 20/09/2026)

| # | Pendiente | Resolución |
|---|---|---|
| 2 | Duración del sprint y forma de acreditar Scrum en este parcial | Confirmado con el docente: **2 semanas por sprint**, igual para todos los sprints |
| 4 | Herramienta de gestión y herramienta CASE | Gestión: **Jira**. CASE: **Enterprise Architect** (`docs/sw1.eap`) |
| 5 | Aplicación de la demostración | Confirmado: **Juice Shop v17.3.0**, ya desplegada (`infra/compose/app-protegida.yaml`) |
| 6 | Confirmar la prioridad Alta de Pb-20, Pb-27 y Pb-28 | Confirmada de facto: las tres se implementaron en el Sprint 1 con prioridad Alta |
| 8 | Si el clasificador basta como "IA personalizada" o debe incluirse el modelo de lenguaje | Confirmado con el docente: el clasificador local (TF-IDF, Pb-20) **ya cumple** el requisito técnico 1; el LLM no es obligatorio. El equipo decide implementar Ollama en el Sprint 2 (Pb-19) como mejora, no como condición |
| 9 | Tecnología del móvil (Flutter vs Expo) | Confirmado: **Flutter**, ya implementado (`movil/lib/`) |
| 10 | Pb-6 con 10 criterios: ¿dividir en dos historias? | No se dividió: se implementó como una sola HU con sus 10 criterios |

### 5.2 Siguen abiertas

| # | Pendiente | Propuesta por defecto |
|---|---|---|
| 1 | PHU de las 13 HU y capacidad del equipo | Planning Poker (C-50) |
| 3 | Product Owner, Scrum Master, desarrolladores y cliente clave | **[POR DEFINIR]** (C-01) |
| 7 | Umbral aceptable de latencia añadida (RNF-02) y meta mínima del clasificador | **[POR DEFINIR]**; medir con k6 (`pruebas/guion.md`) antes de fijar el valor |
