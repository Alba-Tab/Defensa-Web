# Evidencia breve del Sprint 1

Fecha de ejecución: 20 de septiembre de 2026.

## Resultado por historia

| HU | Resultado esencial verificado |
|---|---|
| Pb-1 | Login JWT de 8 horas, hash Argon2, protección de todas las rutas y bloqueo 429 durante 5 minutos. |
| Pb-2 | Regla SQLi validada con Suricata sobre un PCAP; eventos completos, UTC y lectura posterior a rotación. |
| Pb-3 | SQLi recibe reinicio TCP y no llega a la aplicación; tráfico legítimo responde 200. Medidas en `Pb-3.md`. |
| Pb-4 | Con Suricata detenido, la cola nftables con `bypass` deja pasar HTTP; al reiniciarlo vuelve a descartar SQLi. |
| Pb-5 | Una ráfaga de 300 eventos iguales forma un incidente; IP o categoría distintas forman incidentes separados. |
| Pb-6 | Cinco eventos en 60 s crean un bloqueo de 10 minutos; lista blanca, fallo, reintento y conciliación quedan probados. |
| Pb-7 | Informe local con las cuatro secciones requeridas y estado real de la acción defensiva; no depende de un servicio externo. |
| Pb-20 | `entrenar.py` entrenó y exportó `clasificador.joblib`; el backend y la imagen Docker cargan el modelo. La muestra sintética obtuvo precisión y recall SQLi de 1,0; no se presenta como evaluación sobre datos reales. |
| Pb-8 | APK instalado en Android, login real contra el contenedor, token seguro, interceptor Bearer y cierre de sesión ante 401. |
| Pb-9 | Firebase Android validado; el emulador obtuvo y registró un token real. Idempotencia, renovación, permiso rechazado y eliminación de token inválido tienen prueba automatizada. |
| Pb-10 | Cinco SQLi generaron un incidente de severidad 3 y Android recibió la notificación del sistema `Incidente de severidad 3`. También están probados no duplicar, escalar, SSE y datos mínimos. |
| Pb-27 | Lista, detalle, eventos capturados e informe se muestran con widgets `Text`; navegación desde alerta implementada. |
| Pb-28 | Liberación confirmada, idempotente y auditada con el actor administrador. |

## Comprobaciones de integración

- `make PYTHON=.venv/bin/python check-all`: ruff, formato, mypy estricto, 37 pruebas backend, análisis Flutter y 5 pruebas Flutter correctos.
- Migración sobre SQLite vacío: `0001` a `0005` correctas.
- Imagen `sw2_primerparcial-backend`: construida y arrancada; login y salud autenticada correctos; componentes activos `ClasificadorJoblib` y `NotificadorFirebase`.
- `google-services.json`: presente fuera de Git y correspondiente a `bo.uagrm.grupo13.defensa_movil`.
- APK debug con `FCM_HABILITADO=true`: compilado, instalado y abierto sin excepción.
- Pantalla `/configuracion`: abierta en el emulador; mostró servidor, guardado y activación de Firebase.

## Alcance pendiente de evidencia física

La entrega FCM se demostró en un emulador Android con Google Play y la app en segundo plano. El criterio literal de Pb-10 que exige un **teléfono Android real con la app cerrada** todavía requiere repetir el mismo guion en hardware físico. Esto no exige cambios de código, pero no debe darse por demostrado hasta ejecutar esa prueba.

El laboratorio Suricata/nftables/Fail-open se ejecutó en contenedores Linux aislados. La repetición sobre la VM Ubuntu 24.04 del equipo sigue siendo la evidencia final específica del entorno de despliegue.
