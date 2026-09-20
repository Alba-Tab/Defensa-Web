# PROMPT DE CONTEXTO — Plataforma de Defensa Web en Tiempo de Ejecución (Grupo 13, IS2)

> Documento pensado para pegarse como contexto en una conversación con una IA. Contiene todo lo necesario para generar los artefactos del **Sprint 0** sin inventar datos. Lo que no está decidido figura como **[POR DEFINIR]** o en la sección 11 (decisiones abiertas).

---

## 0. Instrucciones para la IA

- **Rol:** analista y arquitecto de software del Grupo 13, asistiendo en el Sprint 0 de un proyecto Scrum.
- **Idioma:** español. Redacción formal y sencilla.
- **Fuente de verdad:** este documento. No inventes herramientas, cifras ni decisiones. Si falta un dato, escribe **[POR DEFINIR]** y propón un valor por defecto aparte.
- **Documentos formales:** sin comparaciones con otros grupos y sin repartir tareas por integrante.
- **Formatos Scrum:** los de la guía del docente (*Un enfoque de aplicación de Scrum*, ver. 3.0): Product Backlog F3, tarjeta de Historia de Usuario F4, Sprint Backlog F5, actas de revisión F1 y de retrospectiva F2.
- **Modelos:** UML 2.5+ para clases y secuencia; **C4** exclusivamente para arquitectura (niveles 1, 2 y 3). Se generan con herramienta CASE.
- **Aún no generar casos de uso.** Corresponden a otra fase.
- **Nunca proponer:** IA en la nube, integrar código dentro de la aplicación protegida, ni herramientas fuera de las listadas sin marcarlas como *propuesta*.

---

## 1. Contexto académico y restricciones

| Aspecto | Definición |
|---|---|
| Materia | Ingeniería de Software II, UAGRM, Grupo 13 (5 integrantes, todos con equipos Windows) |
| Tema asignado | Pruebas web con enfoque de defensa (sombrero blanco) |
| Entregable | Primer Parcial: investigación + 3 casos de estudio locales; **2 llegan hasta diseño, 1 hasta implementación** (este documento describe el implementado) |
| Proceso | **Scrum obligatorio** en el parcial |
| Fecha de entrega | **22 de septiembre de 2026** (exposición de 40–45 min) |
| Requisito técnico 1 | Usar **IA local, entrenada de forma personalizada, que funcione sin conexión a un servidor** |
| Requisito técnico 2 | Existir una **aplicación móvil pertinente** al tema (usar sensores cuando tenga sentido) |
| Valorado | Reportes generativos en tiempo real; interfaz de tipo asistente conversacional |
| Caso local | Cada caso debe ubicarse en un escenario de nuestro medio: **[POR DEFINIR]** (propuesta: comercio electrónico de una pyme) |

> **Decisión de equipo (actualización, cerrada tras consulta al docente el 20/09/2026):** el Requisito técnico 1 exige IA local. El docente confirmó que **no es necesario un LLM**: el clasificador entrenado localmente (TF-IDF + modelo scikit-learn, HU Pb-20) **ya cuenta** como la IA local personalizada que exige el parcial. Aun así, el equipo decide implementar Ollama en el **Sprint 2** (HU Pb-19) como mejora del informe, no como condición para cumplir el requisito. Mientras Ollama no esté listo, el generador de informes sigue usando **OpenRouter (API en la nube) solo para pruebas de laboratorio**, con `GeneradorPlantilla` como respaldo automático si no hay clave configurada o la llamada falla, documentado también en `Modelo_datos.md` (campo `incidente.modelo_informe`).

---

## 2. Objetivo del producto

Plataforma que se ubica **delante** de una aplicación web ya desplegada, inspecciona el tráfico HTTP que la alcanza, **bloquea** las peticiones y direcciones maliciosas, agrupa los eventos en incidentes y los explica en lenguaje natural con IA local, permitiendo al administrador supervisar y liberar bloqueos desde un panel web y una aplicación móvil. **No modifica la aplicación protegida.**

---

## 3. Qué hace y qué no hace

**Hace**
1. Recibe todo el tráfico de la aplicación como única puerta de entrada.
2. Inspecciona el contenido de cada petición y descarta las que coinciden con firmas de ataque.
3. Bloquea temporalmente las direcciones reincidentes en el firewall.
4. Agrupa eventos en incidentes y conserva el historial.
5. Clasifica la severidad y redacta una ficha del incidente con IA local, sin internet.
6. Muestra el estado en un panel web y notifica incidentes críticos al celular.

**No hace**
- Análisis estático del código de la aplicación.
- Corrección automática de vulnerabilidades.
- Detección de fallas de lógica de negocio que requieren conocer el estado interno (IDOR/BOLA, abuso de un JWT válido). Es una limitación consciente del enfoque perimetral.
- Registro dinámico de varias aplicaciones: **la aplicación protegida se configura una vez al desplegar**. El gateway multiaplicación queda como visión y ampliación.

---

## 4. Módulos y requisitos (versión vigente)

| Módulo | Requisitos funcionales |
|---|---|
| **M1. Enrutamiento** | **RF-01** Recibir el tráfico y reenviarlo al destino interno, terminando el TLS. **RF-02** Identificar la IP real del cliente y limitar la tasa de peticiones por origen |
| **M2. Inspección y bloqueo en línea** | **RF-03** Inspeccionar cada petición HTTP contra firmas y descartar las de alta confianza. **RF-04** Registrar cada evento en formato estructurado |
| **M3. Respuesta por dirección** | **RF-05** Bloquear temporalmente una IP que supere un umbral de eventos en una ventana, con duración progresiva ante reincidencia. **RF-06** Mantener lista blanca y permitir liberación manual |
| **M4. Correlación y persistencia** | **RF-07** Consumir eventos y agruparlos en incidentes. **RF-08** Conservar historial consultable por fecha, origen y severidad, expuesto por API autenticada |
| **M5. IA local** | **RF-09** Clasificar la severidad con un modelo entrenado localmente. **RF-10** Generar un informe en lenguaje natural con categoría OWASP y recomendaciones |
| **M6. Panel web** | **RF-11** Mostrar alertas en tiempo real, métricas, historial y **estado de los componentes**. **RF-12** Liberar bloqueos |
| **M7. Móvil** | **RF-13** Notificar incidentes de severidad alta o crítica y consultar su informe. **RF-14** Liberar un bloqueo de forma remota |

**Requisitos no funcionales**
- **RNF-01 Disponibilidad:** si el motor de inspección falla, el tráfico continúa hacia la aplicación (fail-open).
- **RNF-02 Rendimiento:** latencia añadida acotada y medible.
- **RNF-03 Operación sin conexión:** la IA funciona sin internet.
- **RNF-04 Seguridad:** toda acción que modifique el firewall exige autenticación y queda registrada.

---

## 5. Herramientas y qué función usamos de cada una

### 5.1 Capa defensiva (herramientas existentes)

| Herramienta | Rol | Funciones que se usan |
|---|---|---|
| **nginx** | Proxy inverso, borde | `proxy_pass`, terminación TLS, `limit_req`, `real_ip_header` / `set_real_ip_from`, log de acceso |
| **Suricata** (7.x u 8.x, repositorio oficial OISF) | Inspección de tráfico | Modo IDS primero y luego IPS con NFQUEUE; `suricata-update` con Emerging Threats Open; `local.rules`; `drop.conf`; salida `eve.json`; `suricata -T` para validar configuración |
| **Fail2ban** | Castigo por IP | Filtros y jails (`maxretry`, `findtime`, `bantime`, `ignoreip`), `bantime.increment`, `fail2ban-regex`, `fail2ban-client status / set banip / unbanip` |
| **nftables** | Firewall del kernel | Cola hacia Suricata con opción *bypass*; reglas o sets de bloqueo gestionados por Fail2ban |

**Los 3 videos de la exposición (propuesta):** Suricata, Fail2ban y nginx. nftables aparece dentro del video de Fail2ban (`nft list ruleset` antes, durante y después del baneo). Cada video muestra primero la herramienta sola y luego dentro de la plataforma.

### 5.2 Desarrollo propio

| Herramienta | Uso |
|---|---|
| Python + **FastAPI** | Servicio único: ingesta, correlación, decisión, API y panel |
| **SQLite + SQLModel** | Persistencia (modo WAL) |
| **Jinja2 + HTMX + Alpine.js** | Panel web servido por el mismo servicio; SSE para tiempo real |
| **Chart.js** | Gráficos del panel |
| **Flutter (Dart)** | Aplicación móvil multiplataforma (un solo código para Android e iOS) |
| **Firebase Cloud Messaging (FCM)** + `firebase-admin` (Python) | Notificaciones remotas por la API HTTP v1 (requiere internet); respaldo: SSE con la app abierta |
| Stack Flutter (*propuesta*) | `flutter_riverpod` (estado e inyección de dependencias), `dio` (cliente HTTP con interceptor del token), `go_router` (navegación, abre el incidente desde la notificación), `flutter_secure_storage` (token de la API), `local_auth` (biometría antes de liberar un bloqueo), `speech_to_text` (consulta por voz, ampliación) |
| **scikit-learn** | Clasificador de peticiones, exportado con joblib |
| **Ollama** | Modelo de lenguaje pequeño (orden de 1 a 3 B de parámetros; modelo concreto **[POR DEFINIR]**) para redactar la ficha |
| **watchfiles** | Lectura continua de `eve.json` |

### 5.3 Entorno y validación

| Herramienta | Uso |
|---|---|
| VM **Ubuntu Server 24.04 LTS** (2 vCPU, 4 GB RAM, 25 GB) | Ejecuta toda la capa defensiva (requiere Linux) |
| VirtualBox o Hyper-V, red **bridged o host-only** (nunca NAT) | Virtualización |
| Vagrant o script de aprovisionamiento versionado | Entornos idénticos para los 5 equipos |
| Docker Compose | Aplicación protegida |
| Git + GitHub | Control de versiones |
| OWASP ZAP, Nikto, sqlmap, script propio de fuerza bruta | Ataques simulados |
| Grafana k6 | Carga y latencia con y sin Suricata |

---

## 6. Arquitectura (notación C4)

> Cada diagrama debe llevar leyenda y no mezclar niveles. Las relaciones se nombran con verbo + protocolo.

### 6.1 Nivel 1 — Contexto

| Elemento | Tipo | Descripción |
|---|---|---|
| Administrador de seguridad | Persona | Supervisa incidentes y libera bloqueos |
| Cliente legítimo | Persona | Usa la aplicación protegida |
| Origen malicioso | Persona (externa) | Intenta atacar la aplicación |
| **Plataforma de Defensa Web** | Sistema en estudio | Caja única |
| Aplicación web protegida | Sistema externo | Tienda o aplicación de terceros, sin modificar |
| Firebase Cloud Messaging (FCM) | Sistema externo (Google) | Entrega notificaciones push (opcional, requiere internet) |
| Repositorio de reglas Emerging Threats Open | Sistema externo | Fuente de firmas, solo al actualizar |

**Relaciones:** Cliente y Origen malicioso *envían peticiones a* la Plataforma [HTTPS]. La Plataforma *reenvía peticiones legítimas a* la Aplicación [HTTP]. El Administrador *supervisa y libera bloqueos en* la Plataforma [web y móvil]. La Plataforma *solicita notificaciones a* Firebase Cloud Messaging [HTTPS] y *descarga firmas de* Emerging Threats [HTTPS].

### 6.2 Nivel 2 — Contenedores

| Contenedor | Tecnología | Responsabilidad |
|---|---|---|
| Proxy inverso | nginx | TLS, límite de tasa, IP real, reenvío; escribe `access.log` |
| Motor IPS | Suricata (NFQUEUE) | Inspecciona, descarta, escribe `eve.json` |
| Respuesta por IP | Fail2ban | Cuenta eventos, decide baneo temporal |
| Firewall | nftables | Aplica los bloqueos y envía el tráfico a la cola de Suricata |
| Archivos de eventos | `eve.json`, `access.log` | Almacén intermedio de eventos |
| **Servicio de defensa** | Python, FastAPI | Ingesta, correlación, decisión, API, panel |
| Base de datos | SQLite | Incidentes, baneos, auditoría, dispositivos |
| Servicio de IA local | Ollama | Redacta la ficha del incidente |
| Panel web | HTML + HTMX (en el navegador) | Monitoreo y operación |
| App móvil | Flutter (Dart) | Notificación y respuesta remota |

**Relaciones clave:** Proxy *reenvía peticiones a* la Aplicación [HTTP]. Motor IPS *escribe eventos en* `eve.json` [JSON por línea]. Servicio de defensa *lee* `eve.json` [archivo] y *ordena bloqueos a* Fail2ban [`fail2ban-client`, socket local]. Fail2ban *lee* `access.log` y *crea y elimina reglas en* nftables. Servicio de defensa *lee y escribe* en SQLite [SQL] y *solicita informes a* Ollama [HTTP, puerto local]. Panel y app móvil *consultan* al Servicio [HTTP JSON; SSE].

### 6.3 Nivel 3 — Componentes del Servicio de defensa

| Componente | Responsabilidad |
|---|---|
| Fuente de eventos | Interfaz con dos implementaciones: `EveSource` (real) y `FakeSource` (simulada) |
| Correlador | Agrupa eventos en incidentes (misma IP + misma categoría dentro de la ventana) |
| Motor de políticas | Aplica umbral, reincidencia y lista blanca; decide el bloqueo |
| Actuador de bloqueo | Interfaz con `Fail2banActuator` (real) y `DryRunActuator` (solo registra) |
| Clasificador | Modelo scikit-learn: tipo de ataque y confianza |
| Generador de informes | Cliente de Ollama con **plantilla de respaldo** |
| Notificador | FCM (`firebase-admin`) y SSE |
| API REST y vistas web | Endpoints JSON y plantillas HTMX, protegidos con autenticación |
| Repositorio | Acceso a SQLite (SQLModel) |
| Conciliador | Al arrancar y periódicamente, contrasta los baneos de la base con el estado real de Fail2ban y expira los vencidos |
| Configuración | Modo real o simulado, umbrales, rutas |

### 6.4 Vista de despliegue

- **VM Ubuntu Server:** nginx (80/443, público), aplicación protegida (Docker, solo red interna), Suricata, Fail2ban, nftables, servicio de defensa (**puerto 8000, plano de gestión, accesible solo desde la red de administración**).
- **Equipo anfitrión (Windows):** navegador con el panel, editor de código, herramientas de ataque y, por defecto, **Ollama** (la VM lo consulta por la red host-only).
- **Teléfono:** app Flutter (APK), conectado a la misma red (punto de acceso del portátil en la demostración, con salida a internet para recibir las notificaciones de FCM).

### 6.5 Flujo principal

1. La petición llega al firewall: si la IP está baneada, se corta ahí.
2. nginx descifra el TLS y reenvía en HTTP plano.
3. Suricata inspecciona; si coincide con una firma de alta confianza, descarta.
4. Suricata escribe el evento en `eve.json`.
5. El servicio lo lee, lo agrupa en un incidente y evalúa la política.
6. Si se supera el umbral, ordena el baneo a Fail2ban.
7. La IA (asíncrona) clasifica y redacta la ficha. **Nunca decide bloquear.**
8. Si la severidad es alta o crítica, se notifica al móvil.
9. El administrador puede liberar el bloqueo desde el panel o el móvil.

### 6.6 Modelo de datos conceptual (diagrama de clases)

| Clase | Atributos principales | Relaciones |
|---|---|---|
| AplicacionProtegida | nombre, destino_interno, punto_entrada | 1 tiene N Incidente |
| Evento | fecha_utc, ip_origen, sid, firma, categoria, severidad_firma, metodo, url | N pertenecen a 1 Incidente |
| Incidente | ip_origen, tipo_ataque, severidad, estado, inicio, ultima_actividad, categoria_owasp, informe, origen_informe | 1 puede generar 0..N Baneo |
| Baneo | ip, inicio, expira, nivel_reincidencia, estado | N pertenecen a 1 Incidente |
| ListaBlanca | ip_o_red, descripcion | independiente |
| Dispositivo | token_fcm, plataforma, alta, actualizado_en | independiente |
| Auditoria | fecha_utc, actor, accion, ip_afectada, detalle | independiente |
| Usuario | nombre, hash_contrasena | 1 genera N Auditoria |

**Estados:** Incidente = `abierto` → `cerrado`. Baneo = `vigente` → `expirado` | `liberado` | `fallido`. Informe = `generado_ia` | `plantilla`.

> **Nota:** el esquema real y definitivo está en `Modelo_datos.md` (fuente de verdad para el modelo de datos); esta tabla es la descripción conceptual original y puede diferir en detalles menores (p. ej. el campo se llama `actor`, no `usuario`).

---

## 7. Reglas de negocio y valores iniciales (a calibrar en pruebas)

| Regla | Valor inicial |
|---|---|
| Umbral de bloqueo | 5 eventos de severidad media o mayor, misma IP, en 60 s |
| Duración del primer baneo | 10 minutos |
| Reincidencia | Cada baneo dobla la duración; tope 24 h |
| Fuerza bruta de login | 5 respuestas 401/403 al login en 60 s (filtro Fail2ban sobre `access.log`) |
| Agrupación en incidentes | Misma IP + misma categoría dentro de 5 min |
| Cierre de incidente | Sin baneo vigente y sin eventos nuevos en 5 min |
| Severidad de la firma | 1 = alta, 2 = media, 3 = baja (según `alert.severity` de Suricata) |
| Severidad final | La mayor entre la de la firma y la del clasificador; **crítica** = alta + reincidente |
| Notificación push | Solo alta o crítica; una al abrir el incidente y otra si escala |
| Tiempo máximo de la IA | 20 s; luego se usa la plantilla |
| Retención | Incidentes permanentes; eventos crudos 30 días |
| Acciones `drop` | Solo firmas de alta confianza; el resto queda en alerta |
| Lista blanca | Nunca se bloquea: loopback, red de administración, gateway |
| Rate limit nginx | Orientativo: 10 req/s por IP con ráfaga de 20; login 5 req/min |

**Categorías OWASP Top 10:2025 (mapeo inicial):** inyección (SQL, XSS, comandos) → A05; fuerza bruta → A07; path traversal → A01 (verificar); sondeo de archivos de configuración → A02.

**Tipos de ataque a detectar (MVP):** inyección SQL, XSS, path traversal, escaneo y reconocimiento, sondeo de archivos sensibles, fuerza bruta de login.

---

## 8. IA local

**Clasificador (el modelo "entrenado personalizado")**
- Entrada: método, URI decodificada, parámetros, fragmento del cuerpo, user-agent y categoría de la firma.
- Salida: `{benigno, sqli, xss, traversal, escaneo, fuerza_bruta, indeterminado}` + confianza. Bajo un umbral de confianza (propuesta 0,6) se devuelve `indeterminado` y prevalece la severidad de la firma.
- Modelo: TF-IDF de n-gramas de caracteres + regresión logística o Random Forest.
- Datos: HTTP CSIC 2010 (etiquetas normal/anómalo; **verificar disponibilidad y licencia**) más tráfico propio del laboratorio etiquetado por herramienta de ataque, más navegación legítima registrada en la aplicación demo.
- Evaluación: precisión, exhaustividad y matriz de confusión por clase, con partición entrenamiento/prueba.

**Generador de ficha (Ollama)**
- Prompt con solo los hechos del incidente; salida con secciones fijas: *qué ocurrió*, *categoría OWASP*, *acción aplicada*, *recomendaciones*.
- Validación de que la salida contiene las secciones; si no, o si excede el tiempo, se usa la plantilla y se marca `origen_informe = plantilla`.
- Se muestra siempre la etiqueta "generado por IA".
- **Pendiente de confirmar con el docente** si un LLM con prompt estructurado cuenta como "personalizado", o si basta el clasificador entrenado.

---

## 9. Panel, API y móvil

**Panel web:** inicio de sesión · tablero (incidentes por hora, bloqueos vigentes, tipos de ataque, top de IPs, estado de componentes) · alertas en vivo · incidentes (filtros y detalle con ficha) · bloqueos (liberar) · ajustes de solo lectura.

**Móvil:** configuración del servidor (IP editable) · lista de incidentes · detalle con ficha · bloqueos vigentes con botón **Liberar** · notificaciones. Ampliación valorada: consulta por voz sobre el estado ("¿qué pasó anoche?") con reconocimiento del dispositivo.

**API (JSON, autenticada):**
`POST /api/auth/login` · `GET /api/incidentes` · `GET /api/incidentes/{id}` · `GET /api/baneos` · `POST /api/baneos/{ip}/liberar` · `GET /api/metricas` · `GET /api/salud` · `GET /api/eventos` (SSE) · `POST /api/dispositivos`.

---

## 10. Aplicaciones candidatas para la demostración

Criterios: se levanta rápido con Docker, poco consumo de RAM, tiene login (fuerza bruta), tiene parámetros que viajan por la URL (inyección y XSS visibles), funciona en HTTP plano, mantenimiento activo. **Verificar versiones, imágenes y licencias en los repositorios oficiales antes de elegir.**

| Aplicación | Tecnología | Ventajas | Inconvenientes |
|---|---|---|---|
| **OWASP Juice Shop** | Node.js + Angular | Temática de tienda; un solo contenedor; vulnerable a propósito (muestra el daño evitado); login y búsqueda | SPA: el XSS por fragmento `#` no llega al servidor; el login es JSON (fuerza bruta con script propio) |
| **DVWA** | PHP + MariaDB | Formularios clásicos GET/POST, ideales para reglas simples | No es comercio electrónico; requiere base de datos; interfaz antigua |
| **WordPress + WooCommerce** | PHP + MariaDB | Muy realista para una pyme; `wp-login.php` es objetivo típico de fuerza bruta | Más pesado; superficie grande |
| **OpenCart** | PHP + MySQL | Comercio electrónico real y liviano | Asistente de instalación; no es vulnerable por defecto (solo se muestra detección) |
| **PrestaShop** | PHP + MySQL | Comercio electrónico real, imagen oficial | El más pesado del grupo |
| WebGoat, Mutillidae | Java / PHP | Didácticas | Menos alineadas con el escenario de tienda |

**Recomendación por defecto:** Juice Shop como aplicación de la demostración (despliegue inmediato y ataques visibles) y, si hay tiempo, **una segunda aplicación realista** (WooCommerce u OpenCart) para sostener el escenario local.

**Decisión en 30 minutos:** levantar las dos o tres finalistas en la VM y comprobar: (1) responde por HTTP desde el portátil, (2) tiene login, (3) tiene un parámetro GET de búsqueda, (4) consumo de RAM con `docker stats`, (5) se puede reiniciar a estado limpio en menos de un minuto.

> Las aplicaciones vulnerables **nunca** se exponen fuera de la VM ni de la red del laboratorio.

---

## 11. Excepciones y casos límite (y su tratamiento)

| Situación | Riesgo | Tratamiento definido |
|---|---|---|
| HTTPS sin terminar en nginx | Las reglas de contenido no ven nada | Terminar TLS en nginx e inspeccionar el tramo descifrado |
| XSS por fragmento `#` | No viaja al servidor | Documentar como límite; demostrar solo vectores por URI o cuerpo |
| Codificaciones dobles o cuerpos grandes | Evasión de firmas | Incluir pruebas con codificación; documentar el límite de inspección del cuerpo |
| IPv6 sin inspección | Camino que rodea la defensa | Deshabilitar IPv6 en la VM del MVP |
| Detrás de proxy o CDN | Se banea la IP del proxy | `real_ip` solo desde proxies confiables; validar la cabecera de reenvío |
| NAT de VirtualBox en el laboratorio | Todo llega como una sola IP | Red bridged o host-only; verificar en el log la IP real del atacante |
| Usuarios tras una misma IP (CGNAT) | Bloqueo de inocentes | Baneos cortos y liberación rápida desde el móvil |
| Baneo de la IP propia | Perder acceso | `ignoreip` y lista blanca; la API rechaza banear IPs en lista blanca |
| Suricata caído | Sin defensa | Fail-open (*bypass*), estado degradado en el panel (latido con eventos `stats` si están habilitados) |
| Regla mal afinada | Se descarta tráfico legítimo | Empezar en IDS; pocas reglas `drop`; probar con navegación normal antes de activar |
| Paquete descartado | El cliente queda esperando en vez de recibir error | Evaluar acción `reject` para cierre inmediato; explicarlo en la demo |
| Checksums en la VM | Nada dispara o se descarta de más | Revisar validación y offloading de checksums si hay síntomas |
| ET Open completo en 4 GB | Consumo alto | Habilitar solo categorías web; medir con k6 |
| Reglas sin internet | No se actualizan | Descargarlas antes; funciona con reglas en caché |
| Orden de reglas del firewall | Baneos que no se aplican antes de la cola | Verificar con `nft list ruleset` |
| Fail2ban no aplica el baneo | Estado inconsistente | Marcar `fallido`, reintentar, notificar; el conciliador contrasta al arrancar |
| Desbloqueo de IP ya libre | Error innecesario | Operación idempotente |
| Rotación de `eve.json` | El lector se queda mirando el archivo viejo | Detectar rotación y reabrir; probar con `logrotate` |
| Ráfagas (sqlmap) | Saturar la ingesta | Agrupar, cola acotada, deduplicar; la IA nunca bloquea el hilo de lectura |
| Escrituras concurrentes en SQLite | Bloqueos de base | Modo WAL y transacciones cortas |
| Zonas horarias | Fechas incoherentes | UTC en base de datos; conversión al mostrar |
| IA lenta, caída o que inventa | Ficha incorrecta o ausente | Timeout, plantilla de respaldo, validación de secciones, etiqueta "generado por IA" |
| Inyección de prompt en el payload capturado | El atacante manipula al modelo | El payload va como dato delimitado y truncado; la salida del modelo nunca ejecuta acciones |
| Panel o API expuestos al atacante | Ataque a la defensa | Puerto de gestión aparte, solo red de administración, autenticación, límite de intentos de login |
| IP recibida como comando | Inyección de comandos | Validar con `ipaddress`; `subprocess` con lista de argumentos, nunca `shell=True` |
| Servicio con privilegios | Escalada | Usuario dedicado + `sudoers` limitado a los comandos exactos de `fail2ban-client` |
| Secretos y token robado | Acceso indebido | Variables de entorno fuera del repositorio (incluida la ruta de la clave JSON de la cuenta de servicio de Firebase); tokens con expiración; revocar dispositivo |
| Celular sin alcance a la VM | Demo caída | Punto de acceso del portátil; IP del servidor configurable en la app |
| Push sin internet, token FCM rotado o inválido | No llega la alerta | SSE con la app abierta; actualizar el token con `onTokenRefresh` (por eso `actualizado_en`); eliminar el dispositivo si FCM responde `UNREGISTERED` |
| Servicio de defensa sin salida a internet | No puede llamar a FCM y no llegan las notificaciones | Red bridged con salida a internet, o un segundo adaptador NAT solo para esa salida (el tráfico de ataque sigue por la interfaz bridged o host-only); el punto de acceso del portátil debe compartir conexión con el teléfono |
| Android bloquea HTTP plano (desde Android 9) | La app no alcanza el panel ni la API dentro del laboratorio | Permitir HTTP con `usesCleartextTraffic` o con una `network_security_config` limitada a la IP del laboratorio |
| Falla de red en el aula | Demo imposible | Video de respaldo grabado, modo demostración, respuestas de IA precargadas, ensayo previo desde cero |

---

## 12. Plan de pruebas (ataque simulado → señal esperada)

| Ataque | Herramienta | Resultado esperado |
|---|---|---|
| Inyección SQL en búsqueda | sqlmap | Petición descartada, incidente creado, categoría A05 |
| XSS por parámetro | curl / ZAP | Regla propia dispara, petición descartada |
| Path traversal | curl / ffuf | Descarte e incidente |
| Escaneo de rutas | Nikto, ffuf | Baneo tras superar el umbral |
| Sondeo de archivos sensibles | curl | Alerta y, si reincide, baneo |
| Fuerza bruta de login | Script propio | Baneo en la ventana definida |
| Navegación legítima prolongada | Navegador / k6 | **Cero** bloqueos (falsos positivos) |
| IP en lista blanca atacando | curl | Alerta sin baneo |
| Suricata detenido con tráfico | `systemctl stop` | La aplicación sigue respondiendo |
| Vencimiento y liberación | Reloj / móvil | La regla desaparece y se registra la acción |

**Métricas a reportar:** tasa de detección, tasa de falsos positivos, tiempo desde el primer evento hasta la regla de firewall, latencia añadida (k6 con y sin Suricata), calidad de la categoría OWASP asignada.

---

## 13. Cierre del Sprint 0 (actividades a–i de la guía del docente)

| Actividad | Estado y contenido disponible |
|---|---|
| **a) Equipo Scrum** | Scrum Master, Product Owner y desarrolladores: **[POR DEFINIR]**. Stakeholder o cliente clave: **[POR DEFINIR]** |
| **b) Objetivo del producto** | Sección 2 |
| **c) Requerimientos iniciales** | Sección 4. Épicas candidatas = módulos M1 a M7 |
| **d) Duración del sprint** | **Resuelto con el docente (20/09/2026): 2 semanas por sprint**, igual para todos los sprints; la entrega es el 22/09 |
| **e) Infraestructura** | Sección 5. Gestión del proyecto: **Jira** |
| **f) Patrón de desarrollo** | Rama `main` protegida y ramas `feature/<HU>` con revisión; commits convencionales; PEP 8 con ruff/black en Python y `dart format` y `flutter analyze` en Flutter; pruebas con pytest y `flutter_test`; interfaces `Fuente de eventos` y `Actuador` para el modo simulado |
| **g) Modelos iniciales** | Contexto (C4 nivel 1, 6.1), datos (clases, 6.6), arquitectura (C4 nivel 2, 6.2) |
| **h) Calidad y DoD** | Esenciales: **seguridad e integridad**, **fiabilidad** (fail-open), **eficiencia** (latencia), facilidad de uso, corrección, mantenibilidad (interfaces), portabilidad (VM reproducible). **DoD propuesta:** criterios de aceptación cumplidos; código integrado en `main`; pruebas pasando; verificado en la VM con el ataque del guion; sin secretos en el repositorio; desplegable con un solo comando |
| **i) Product Backlog (F3)** | Generar HU (Como / Quiero / Para, criterios de aceptación, INVEST) a partir de RF-01 a RF-14. **Los PHU los estima el equipo con Planning Poker, no la IA** |

### Decisiones cerradas
Protección en el mismo host con **una aplicación fija** (**Juice Shop v17.3.0**, ya desplegada en `infra/compose/app-protegida.yaml`) · Suricata IPS + Fail2ban + nftables + nginx, insertados en **Modo B** (nginx termina TLS y Suricata inspecciona el tramo HTTP interno descifrado, implementado en Pb-29) · servicio único FastAPI + SQLite · panel HTMX · móvil **Flutter** (Android) con notificaciones FCM · autenticación con usuario administrador único, contraseña con hash y token con expiración de 8 h (implementada) · IA local: el clasificador TF-IDF **ya satisface el requisito técnico 1** (confirmado con el docente); Ollama se agrega en el Sprint 2 (Pb-19) como mejora, no como condición · VM Ubuntu Server en red bridged o host-only · IA siempre posterior a la detección · modo simulado para desarrollar sin VM · escenario local: comercio electrónico de una pyme · duración de sprint: **2 semanas** (confirmado con el docente) · herramienta de gestión: **Jira** · herramienta CASE: **Enterprise Architect** (`docs/sw1.eap`) · videos de la exposición: Suricata, Fail2ban y nginx.

### Decisiones abiertas (con propuesta por defecto)

| # | Decisión | Propuesta por defecto |
|---|---|---|
| 1 | Roles Scrum: Product Owner, Scrum Master, desarrolladores y cliente clave | **[POR DEFINIR]** |
| 2 | Umbral aceptable de latencia añadida (RNF-02) y meta mínima del clasificador para `sqli` | Medir con k6 en la máquina de demostración (`pruebas/guion.md`) antes de fijar el valor |
| 3 | Ubicación de Ollama, una vez implementado en el Sprint 2 | Equipo anfitrión, consultado desde la VM |

### Verificaciones técnicas (spikes) del Sprint 0
Cada una con criterio de éxito verificable el mismo día:
1. **Cola de Suricata:** una petición con un patrón de prueba se descarta y el tráfico normal pasa por el tramo HTTP interno del Modo B.
2. **Fail-open:** detener Suricata no corta la aplicación.
3. **Baneo de extremo a extremo:** un ataque simulado termina en una regla visible en `nft list ruleset` y en una fila de la base.
4. **Lector de eventos:** sobrevive a la rotación de `eve.json`.
5. **IA:** la ficha se genera en menos de 20 s en la máquina de demostración, o se decide el modelo más pequeño.
6. **Alcance móvil:** el teléfono abre el panel por el punto de acceso del portátil.
7. **Push con FCM:** el servicio envía una notificación con `firebase-admin` y llega a un teléfono Android real con la app cerrada; al tocarla se abre el detalle del incidente.

> **Rebanada vertical mínima del primer sprint:** un ataque → detección → incidente en la base → baneo → ficha → notificación. Todo lo demás se construye alrededor de ese hilo.
