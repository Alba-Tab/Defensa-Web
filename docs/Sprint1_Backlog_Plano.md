# Sprint Backlog — Sprint 1

> Las HU del Product Backlog (Pb-*) no son el Sprint Backlog: son la unidad de negociación con el Product Owner. El Sprint Backlog es esta lista de **tareas** (SP-01 en adelante) en las que el equipo las descompuso para ejecutarlas y medir avance día a día.

| ID | Tarea | Estimación (h) | Responsable |
|---|---|---|---|
| SP-01 | Autenticación: modelo de usuario, hash de contraseña y `POST /api/auth/login` con JWT de 8 h | 5 | Aldana |
| SP-02 | Protección de rutas (401 sin token o con token vencido) y límite de intentos de login | 3 | Aldana |
| SP-03 | Instalar y configurar Suricata: IDS, reglas ET Open (categorías web), regla propia de SQLi, `eve.json` y `logrotate` | 6 | Albaro |
| SP-04 | Implementar `EveSource` (sobrevive a la rotación) y guardar las alertas como `Evento` en la base | 5 | Albaro |
| SP-05 | Prueba con sqlmap contra el buscador y pruebas automatizadas de la regla | 3 | Albaro |
| SP-06 | Configurar nftables e IPS: cola con *bypass*, `drop.conf` de alta confianza y acción `reject` | 5 | Noel |
| SP-07 | Prueba de falsos positivos (navegación legítima) y medición de latencia añadida con k6 | 5 | Noel |
| SP-08 | Confirmar el *fail-open* de la cola, implementar el monitor de Suricata y `GET /api/salud` con estado degradado, con prueba | 6 | Brandom |
| SP-09 | Implementar el Correlador: agrupación por IP y categoría (ventana de 5 min), conversión de severidad y cierre automático | 6 | Jairo |
| SP-10 | Endpoints `GET /api/incidentes` y `GET /api/incidentes/{id}`, con pruebas unitarias del Correlador | 4 | Jairo |
| SP-11 | Diseñar e implementar el Motor de políticas (umbral, ventana, duración) y la lista blanca | 6 | Aldana |
| SP-12 | Implementar `Fail2banActuator` (sin `shell=True`), asociar el baneo a su incidente y auditar la acción | 6 | Aldana |
| SP-13 | Implementar el Conciliador (contraste al arrancar, expira vencidos) y pruebas de políticas/conciliador | 4 | Aldana |
| SP-14 | Diseñar la plantilla (4 secciones, tabla OWASP), implementar `GeneradorPlantilla` y disparar la generación al crear el incidente, con prueba | 6 | Albaro |
| SP-15 | Definir el esquema de datos etiquetados, preparar el dataset y el script de captura | 4 | Noel |
| SP-16 | Entrenar el clasificador TF-IDF, exportarlo con joblib e integrar `ClasificadorJoblib` con su umbral de confianza | 6 | Noel |
| SP-17 | Evaluación (precisión, exhaustividad, matriz de confusión) y pruebas del modelo entrenado | 4 | Noel |
| SP-18 | Pantalla de configuración del servidor y pantalla de login con almacenamiento seguro del token | 5 | Albaro |
| SP-19 | Manejo de errores (credenciales inválidas, servidor inalcanzable) y redirección a login cuando el token vence | 3 | Albaro |
| SP-20 | Registro de dispositivo: permiso de notificaciones, `POST /api/dispositivos` sin duplicados, actualización y baja del token FCM | 6 | Albaro |
| SP-21 | Implementar `NotificadorFirebase` y el disparo al abrir un incidente de severidad alta (y si escala) | 5 | Jairo |
| SP-22 | Respaldo por SSE sin internet y manejo de dispositivo inválido durante el envío | 3 | Jairo |
| SP-23 | Lista de incidentes en la app, pantalla de detalle con las 4 secciones y apertura desde la notificación | 6 | Brandom |
| SP-24 | Lista de bloqueos vigentes, liberación idempotente con confirmación en la UI y auditoría | 6 | Aldana |
| **Total** | | **118** | |

## Resumen por responsable

| Responsable | Horas |
|---|---|
| Aldana | 8 + 16 + 6 = **30** |
| Albaro | 14 + 6 + 8 + 6 = **34** |
| Noel | 10 + 14 = **24** |
| Brandom | 6 + 6 = **12** |
| Jairo | 10 + 8 = **18** |
