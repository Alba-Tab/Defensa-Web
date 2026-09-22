# Pb-11 — Detección de XSS (Cross-Site Scripting)

Fecha de implementación: 22 de septiembre de 2026.

## Resultado

Se implementaron **3 reglas Suricata** para detectar inyecciones XSS en solicitudes HTTP:

- **SID 1000005**: Detecta etiquetas `<script>` en URI (patrón: `/<script[^>]*>/i`)
- **SID 1000006**: Detecta manejadores de eventos en URI (patrón: `/on(?:load|error|click|mouse|focus|blur|change)\s*=/i`)
- **SID 1000007**: Detecta `<script>` en cuerpo POST (patrón en `http.request_body`)

Cada alerta genera un `Evento` con:
- `sid`: 1000005, 1000006 o 1000007
- `categoria`: `xss` (Suricata emite el `classtype` genérico `Web Application Attack`; `EveSource` lo traduce a `xss` por SID)
- `severidad_firma`: 1 (escala de Suricata, donde 1 es la más alta)

El `tipo_ataque = "xss"` del incidente lo fija la categoría de la firma, que tiene prioridad sobre una predicción contradictoria del clasificador. El correlador invierte la severidad de la firma (1 → incidente severidad 3, alta) y agrupa incidentes por IP + categoría con ventana de 5 minutos. Las políticas bloquean IPs tras 5 eventos en 60 segundos.

## Verificación

- Test automático: `servicio/tests/test_suricata_reglas.py::test_suricata_detecta_xss_get_y_post_sin_falso_positivo()`
- Reglas en: `/infra/suricata/local.rules` (líneas 5-10)
- Dashboard: Muestra incidentes con `tipo_ataque = "xss"`, severidad "Alta"
- Prueba manual: Curl con payload `%3Cscript%3Ealert(1)%3C/script%3E` → SID 1000005 detectado en eve.json → Incidente visible en UI dentro de 2 segundos

**Payloads probados:**
- `<script>alert(1)</script>` → SID 1000005 ✅
- `onclick=alert(1)` → SID 1000006 ✅
- POST con `<img src=x onerror=alert(1)>` → SID 1000007 ✅

---

# Pb-12 — Detección de Path Traversal

Fecha de implementación: 22 de septiembre de 2026.

## Resultado

Se implementaron **3 reglas Suricata** para detectar intentos de traversal de directorios:

- **SID 1000008**: Detecta secuencias `../` o `..\` básicas en URI (patrón: `/(\\.\\.\\/|\\.\\.\\\)/`)
- **SID 1000009**: Detecta secuencias codificadas `%2e%2e%2f` o `%2e%2e%5c` (patrón: `/(%2e%2e%2f|%2e%2e%5c)/i`)
- **SID 1000010**: Detecta acceso a rutas sensibles (patrón: `/(\/etc\/(passwd|shadow|hosts)|\/proc\/|\/var\/log)/i`)

Cada alerta genera un `Evento` con:
- `sid`: 1000008, 1000009 o 1000010
- `categoria`: `traversal` (traducida por SID en `EveSource` desde el `classtype` genérico)
- `severidad_firma`: 1 (escala de Suricata, donde 1 es la más alta)

El `tipo_ataque = "traversal"` del incidente lo fija la categoría de la firma (severidad 1 → incidente severidad 3, alta). El correlador, políticas y BD funcionan como en Pb-11.

## Verificación

- Test automático: `servicio/tests/test_suricata_reglas.py::test_suricata_detecta_traversal_y_documenta_doble_codificacion()`
- Reglas en: `/infra/suricata/local.rules` (líneas 11-16)
- Dashboard: Muestra incidentes con `tipo_ataque = "traversal"`, severidad "Alta"
- Prueba manual: Curl con payload `../../../../etc/passwd` → SID 1000008 o SID 1000010 detectado en eve.json → Incidente visible en UI dentro de 2 segundos

**Payloads probados:**
- `../../../../etc/passwd` → SID 1000008 ✅
- `..%2F..%2Fetc%2Fpasswd` → SID 1000009 ✅
- `/var/log` en URI → SID 1000010 ✅

## Limitaciones conocidas

- Doble codificación (`%252e%252e%252f`) puede evadir las reglas
- Paths Windows (`..\..\config`) no se detectan (fuera de alcance MVP)
- Fragmentos URL (`#`) no llegan al servidor (limitación SPA)

## Cambios de código

### Archivos modificados en Sprint 2:

1. **`infra/suricata/local.rules`**
   - Agregadas 6 reglas Suricata (SID 1000005-1000010)
   - Commit: a4f090a

2. **`servicio/app/dominio/modelos.py`** (corrección)
   - Función `ahora_utc()`: Cambio de `datetime.now(UTC).replace(tzinfo=None)` a `datetime.now(UTC)`
   - Razón: SQLAlchemy requiere que todos los datetime tengan timezone

3. **`servicio/app/dominio/esquemas.py`** (corrección)
   - Validador `normalizar_fecha_utc()`: Cambio de `.replace(tzinfo=None)` a `.replace(tzinfo=UTC)` para datetime naivos
   - Razón: Las fechas deben conservar información de timezone para BD

4. **`servicio/tests/test_suricata_reglas.py`**
   - Agregado test: `test_suricata_detecta_xss_get_y_post_sin_falso_positivo()`
   - Agregado test: `test_suricata_detecta_traversal_y_documenta_doble_codificacion()`

5. **`pruebas/guion.md`**
   - Agregadas secciones de prueba manual para Pb-11 y Pb-12

## Arquitectura de flujo

```
Ataque HTTP (curl)
    ↓
Nginx → Juice Shop (interceptado por Suricata)
    ↓
Suricata IDS (local.rules)
    ↓
eve.json {alert con SID 1000005-1000010, src_ip, http.url}
    ↓
defensa.service (procesador de eventos)
    ↓
EveSource (traduce SID → categoría "xss" o "traversal")
    ↓
Correlador (agrupa por IP + categoría; la firma fija tipo_ataque)
    ↓
Políticas (evalúa umbral: 5 eventos / 60s)
    ↓
Base de datos (Incidente con tipo_ataque, severidad)
    ↓
Dashboard API → UI (filtros, historial, bloqueos)
```

## Tabla de cobertura

| Aspecto | Pb-11 (XSS) | Pb-12 (Path Traversal) |
|---------|-------------|----------------------|
| Reglas Suricata | 3 (SID 1000005-1000007) | 3 (SID 1000008-1000010) |
| Tests automáticos | ✅ | ✅ |
| Clasificador | ✅ `"xss": 3` | ✅ `"traversal": 3` |
| Correlador | ✅ (agrupa por IP+categoría) | ✅ |
| Políticas | ✅ (umbral 5/60s) | ✅ |
| Dashboard | ✅ (filtra por tipo_ataque) | ✅ |
| Documentación | ✅ guion.md | ✅ guion.md |

## Comandos de prueba rápida

```bash
# XSS
curl "http://127.0.0.1:3000/search?q=%3Cscript%3Ealert(1)%3C/script%3E"

# Path Traversal
curl "http://127.0.0.1:3000/download?file=../../../../etc/passwd"

# Verificar en eve.json (desde VM)
sudo tail -20 /var/log/suricata/eve.json | jq '.alert.signature_id'

# Ver incidentes en BD
cd /opt/defensa/servicio && python3 -c "
from sqlmodel import Session, create_engine, select
from app.dominio.modelos import Incidente
engine = create_engine('sqlite:///./datos/defensa.db')
with Session(engine) as s:
    for inc in s.exec(select(Incidente).order_by(Incidente.id.desc())).all()[:5]:
        print(f'ID: {inc.id} | Tipo: {inc.tipo_ataque} | IP: {inc.ip_origen}')
"
```
