# Plataforma de Defensa Web en Tiempo de Ejecución

Base ejecutable previa al Sprint 1. Incluye modo simulado y real, infraestructura defensiva,
persistencia SQLite, correlación, política de bloqueo, clasificación e informes por plantilla,
notificación FCM y cliente Android.

## Requisitos

- Python 3.12+
- Docker y Docker Compose (opcional)

## Desarrollo local

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e './servicio[dev,real]' -r ia/requirements.txt
cp .env.example .env
make migrate
make run
```

Los comandos se ejecutan desde la raíz del repositorio para que la API y Alembic utilicen la
misma configuración y el mismo archivo de base de datos.

El panel queda en `http://127.0.0.1:8000`; si no hay sesión redirige a `/login`. La documentación
OpenAPI está en `/docs`. Los endpoints operativos, incluido `/api/salud`, exigen Bearer para móvil
o la cookie `HttpOnly` emitida por el login web.

## Verificación

```bash
make check-all
```

La evidencia manual de Pb-2/Pb-3 está en `pruebas/guion.md`. La muestra reproducible de IA, su
reporte y el modelo exportado están en `ia/muestras/`, `ia/resultados/` y `servicio/modelos/`.
Firebase requiere el `google-services.json` del proyecto real del equipo; siga
`movil/FIREBASE.md` y valide con `bash movil/verificar_firebase.sh`.

## Alcance actual

- `FakeSource` y `DryRunActuator` permiten desarrollar sin VM.
- `EveSource` y `Fail2banActuator` conectan Suricata y el firewall en modo real.
- Un evento se agrupa por IP y categoría dentro de una ventana configurable.
- Cinco eventos de severidad media o alta en 60 segundos producen un baneo simulado.
- La lista blanca y los baneos ya vigentes evitan acciones duplicadas.
- El enriquecedor genera la ficha por plantilla y envía FCM para severidad alta. El cliente de
  OpenRouter permanece como componente experimental, pero no está conectado al arranque actual.
- La app Android consume autenticación, incidentes, informes, bloqueos y liberación remota.
- El panel web consume historial filtrable, detalle, SSE, salud, métricas y liberación de bloqueos.

## Modo real

La infraestructura y el orden de despliegue están documentados en `infra/README.md`. El modo
real exige `DEFENSA_JWT_SECRET`, `DEFENSA_ADMIN_PASSWORD`, acceso a `eve.json` y el permiso
limitado de `sudoers` para `fail2ban-client`.

---

## Cómo probar el sistema en tu PC

Guía rápida para el equipo: qué instalar, qué archivos tocar, y cómo comprobar que todo
funciona. Cubre el servicio y la app móvil corriendo en modo **simulado** (sin necesitar la VM
con Suricata/nftables/Fail2ban — eso solo se prueba en `vagrant up`, ver `infra/README.md`).

### 0. Requisitos

| Herramienta | Para qué | Notas |
|---|---|---|
| Git | Clonar el repo | |
| Python 3.12+ | Correr el servicio | En Windows, instalarlo desde python.org (marcar "Add to PATH") |
| Docker Desktop | Alternativa a instalar Python (opcional) | |
| Flutter SDK + Android Studio | Solo si van a probar la app móvil | |
| `make` | Atajos de comandos | En Windows: Git Bash lo trae, o usar WSL2. Si no tienen `make`, cada comando tiene su equivalente manual más abajo |

### 1. Clonar el repositorio

```bash
git clone https://github.com/Alba-Tab/Defensa-Web.git
cd Defensa-Web
```

### 2. Configurar las variables de entorno

```bash
cp .env.example .env
```

Abran `.env` y completen **al menos estos dos campos** (si quedan vacíos, el sistema arranca
pero no se puede iniciar sesión porque no existe usuario administrador):

```
DEFENSA_JWT_SECRET=cualquier-cadena-larga-y-aleatoria
DEFENSA_ADMIN_USUARIO=admin
DEFENSA_ADMIN_PASSWORD=una-clave-para-probar
```

Todo lo demás puede quedar como está — por defecto corre en modo `simulado` (sin Suricata, con
un generador de eventos falso) y sin clasificador de IA ni Firebase ni OpenRouter (esos son
opcionales, ver sección 6).

### 3. Levantar el servicio — elijan una opción

**Opción A: entorno local con Python (recomendada)**

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -e './servicio[dev,real]' -r ia/requirements.txt
make migrate
make run
```

Si no tienen `make`, el equivalente manual es:

```bash
python -m alembic -c servicio/alembic.ini upgrade head
python -m uvicorn app.main:app --app-dir servicio --reload
```

**Opción B: Docker (no necesita instalar Python)**

```bash
docker compose up --build
```

En ambos casos el servicio queda en **`http://127.0.0.1:8000`**.

### 4. Comprobar que funciona

- Documentación interactiva de la API: `http://127.0.0.1:8000/docs`
- Panel web: `http://127.0.0.1:8000/` (redirige al inicio de sesión)
- Estado de salud autenticado: `http://127.0.0.1:8000/api/salud`

Probar el login y un ataque simulado (reemplacen la clave por la que pusieron en `.env`):

```bash
# 1) iniciar sesión y guardar el token en una variable
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"usuario":"admin","contrasena":"una-clave-para-probar"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 2) simular un ataque SQLi (solo funciona en modo simulado)
curl -s -X POST http://127.0.0.1:8000/api/simulacion/eventos \
  -H 'Content-Type: application/json' \
  -d '{"fecha_utc":"2026-09-19T12:00:00","ip_origen":"203.0.113.50","sid":1000001,"firma":"SQLi de prueba","categoria":"web-application-attack","severidad_firma":1,"metodo":"GET","url":"/buscar?q=1 OR 1=1"}'

# 3) ver los incidentes
curl -s http://127.0.0.1:8000/api/incidentes -H "Authorization: Bearer $TOKEN"
```

Si el paso 3 devuelve un incidente con esa IP, el servicio está funcionando de punta a punta.

### 5. Correr la suite automática de pruebas

```bash
make check-all
```

Corre lint, tipos, las pruebas del servicio y análisis/tests de la app móvil. Si todo sale en
verde, el entorno de cada quien está bien configurado.

### 6. Probar la app móvil

```bash
cd movil
flutter pub get
flutter run
```

- **En el emulador de Android**: el campo "Servidor" del login ya viene con
  `http://10.0.2.2:8000` (es la forma en que el emulador ve al `127.0.0.1` de la PC). Con el
  servicio corriendo (paso 3), solo hace falta iniciar sesión con el usuario/clave del `.env`.
- **En un celular físico** (misma red Wi-Fi que la PC): `127.0.0.1` no sirve desde el teléfono.
  Necesitan la IP de la PC en la red local (`ipconfig` en Windows, `ifconfig`/`ip a` en
  Mac/Linux) y arrancar el servicio escuchando en todas las interfaces:
  ```bash
  python -m uvicorn app.main:app --app-dir servicio --host 0.0.0.0 --port 8000
  ```
  (la Opción B con Docker ya escucha así por defecto). Luego, en el campo "Servidor" de la app,
  poner `http://IP_DE_LA_PC:8000`.
- Las notificaciones push (Firebase) están desactivadas por defecto y no hacen falta para
  probar el resto de la app; si alguien quiere activarlas, ver `movil/FIREBASE.md`.

### 7. Piezas opcionales (no bloquean la prueba básica)

| Si quieren probar... | Necesitan configurar en `.env` |
|---|---|
| El clasificador de IA local | `DEFENSA_MODELO_CLASIFICADOR=servicio/modelos/clasificador.joblib` (el modelo de demo ya está en el repo) |
| Cliente experimental de OpenRouter | El componente y sus pruebas existen, pero no se conecta al arranque mientras Pb-19 esté aplazada |
| Notificaciones push reales | Ver `movil/FIREBASE.md` |
| La capa defensiva completa (Suricata, nginx, nftables, Fail2ban) | Necesita Vagrant + VirtualBox — ver `infra/README.md` y correr `vagrant up` |

### Problemas comunes

- **"no such table: usuario"** → falta correr `make migrate` (o el comando manual de Alembic) antes de `make run`.
- **Login devuelve 401 con la clave correcta** → revisen que `DEFENSA_ADMIN_PASSWORD` no haya quedado vacío en `.env`; si estaba vacío cuando arrancó por primera vez, el usuario admin nunca se creó. Borren `datos/defensa.db`, completen la clave, y vuelvan a correr `make migrate && make run`.
- **Puerto 8000 ocupado** → alguien más ya tiene el servicio corriendo en esa terminal; ciérrenlo o usen otro puerto (`--port 8001`).
- **`make` no reconocido en Windows** → usen Git Bash (clic derecho → "Git Bash Here") o instalen `make` con `choco install make`.
