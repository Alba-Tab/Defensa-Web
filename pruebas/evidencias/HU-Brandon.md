# Evidencia de Pb-16 y Pb-17

Rama: `feature/brandon-HU` · VM de laboratorio: `192.168.56.20`.

Las comprobaciones se realizaron el 22 de septiembre de 2026. Se distinguen las
pruebas automatizadas del servicio de las verificaciones en la VM. No se presenta
un resultado esperado como si fuera un resultado observado.

| HU | Resultado | Evidencia |
| --- | --- | --- |
| Pb-16 | Implementada y probada | Progresión 10→20→40 min hasta tope de 24 h, severidad crítica y auditoría, probadas automáticamente y en VM |
| Pb-17 | Implementada y probada | Jail de login sobre `access.log`, incidente `fuerza_bruta`, baneo y liberación autenticada, probados automáticamente y en VM |

## Pb-16 — Bloqueo progresivo

El motor de políticas (`MotorPoliticas.evaluar`) calcula la duración del baneo como
`600 s × 2^nivel_reincidencia`, con tope de 86 400 s (24 h). El `nivel_reincidencia`
es el número de baneos previos de la misma IP en estado `vigente`, `expirado` o
`liberado`.

Decisión documentada (criterio 2): **un baneo liberado manualmente sí cuenta como
reincidencia**. Por eso, tras una liberación desde el panel o el móvil, el siguiente
baneo de esa IP duplica la duración respecto al anterior. Esta elección prioriza
mantener fuera al atacante persistente por encima de reiniciar su historial al
liberarlo.

La severidad del incidente se eleva a `4` (crítica) cuando el incidente ya es de
severidad alta (`>= 3`) y la IP reincide (`nivel >= 1`). Esto habilita la severidad
crítica que la regla de notificaciones de Pb-10 ya contemplaba pero que hasta ahora
nunca podía ocurrir. Al llegar al tope de 24 h, los baneos siguientes mantienen esa
duración sin seguir duplicando.

Cada baneo registra su `nivel_reincidencia` en el detalle (`BaneoSalida`, visible en
el panel) y una auditoría con `nivel_reincidencia` y `duracion_segundos`.

Pruebas automatizadas (`servicio/tests/test_politicas.py`):

- `test_reincidencias_duplican_hasta_tope_y_quedan_auditadas`: una misma IP encadena
  baneos con duraciones `600, 1200, 2400, 4800, 9600, 19200, 38400, 76800, 86400,
  86400` s. Verifica que el segundo baneo con incidente de severidad alta marca
  severidad `4`, que el `nivel_reincidencia` crece con cada baneo y que el último
  registro de auditoría contiene `nivel_reincidencia=9;duracion_segundos=86400`.

Verificación en la VM: la prueba controlada de Pb-17 (abajo) comprueba también los
criterios de Pb-16 sobre el baneo real: duración `600 × 2^nivel`, tope de 24 h y
severidad `4` cuando la IP reincide.

## Pb-17 — Bloqueo por fuerza bruta

Fail2ban decide el baneo sin pasar por Suricata; el servicio lo asocia después al
ciclo de incidentes.

- **Filtro y jail.** El jail `defensa-login` (`infra/fail2ban/jail.local`) lee
  `/var/log/defensa/access.log` con `maxretry = 5` y `findtime = 60`. El filtro
  `defensa-login.conf` reconoce solo las respuestas fallidas del login:
  `failregex = ^\s*DEFENSA_LOGIN ip=<HOST> method=POST path=/api/auth/login status=(?:401|403)$`.
- **Origen del registro.** En modo real, `auth.py` escribe una línea `DEFENSA_LOGIN`
  por cada respuesta 401/403 del login administrativo, con la IP canónica tomada del
  `X-Forwarded-For` que nginx propaga.
- **Baneo.** Al superar el umbral, Fail2ban banea en nftables con
  `banaction = nftables-multiport`, reutilizando la infraestructura de Pb-6.
- **Asociación al incidente.** `DetectorFuerzaBruta.baneados()` consulta el jail de
  login; por cada IP, `procesar_baneo_fuerza_bruta` crea o asocia un incidente con
  `tipo_ataque = fuerza_bruta` y `severidad_firma = 1` (alta), evalúa la política con
  `confirmado_por_fail2ban=True` (satisface que `baneo.incidente_id` sea obligatorio)
  y traslada el baneo al jail principal para que se libere como cualquier otro.
- **Ciclo de vida.** El incidente resultante recibe informe (Pb-7/Pb-19) y notifica
  por su severidad alta (Pb-10), igual que cualquier otro incidente.
- **Lista blanca.** El `ignorecommand` del jail ejecuta `ignorar_ip.py`, que consulta
  la tabla `lista_blanca` antes de que Fail2ban decida; una IP protegida nunca se
  banea por este filtro. Ante un error de base de datos, el script omite el baneo
  (falla seguro).

Pruebas automatizadas:

- `servicio/tests/test_fail2ban_login.py`: el jail exige cinco fallos en 60 s sobre
  `access.log`; el filtro acepta solo `status` 401/403 y rechaza 200/429; el
  `ignorecommand` consulta redes dinámicas de la lista blanca y falla seguro sin base.
- `servicio/tests/test_detector_fuerza_bruta.py`: una IP baneada en el jail de login
  produce un incidente `fuerza_bruta`, el baneo se traslada al jail principal y el
  detector distingue varias IP sin duplicar baneos.
- `servicio/tests/test_api.py::test_login_real_registra_cinco_fallos_para_fail2ban`:
  cinco intentos fallidos escriben cinco líneas `DEFENSA_LOGIN ... status=401` en el
  `access.log` configurado.

Verificación en la VM (`pruebas/verificar_pb17_vm.py`, solo con la IP reservada
`198.51.100.42` de TEST-NET-2):

```bash
cat pruebas/verificar_pb17_vm.py | vagrant ssh -c \
  'cat > /tmp/verificar_pb17_vm.py && sudo /opt/defensa/venv/bin/python /tmp/verificar_pb17_vm.py'
```

Se observó: cinco intentos registrados en el jail de login, baneo en Fail2ban,
incidente `fuerza_bruta` con la duración y severidad de Pb-16, traslado al jail
principal y liberación mediante `POST /api/baneos/{ip}/liberar` autenticada. Salida:
`OK Pb-17: Fail2ban, incidente, baneo y liberación autenticada`.

El criterio 6 (script propio de fuerza bruta) se cubre con esta prueba controlada,
que inyecta los intentos en el jail de login contra una IP de laboratorio reservada
en lugar de forzar credenciales reales.
