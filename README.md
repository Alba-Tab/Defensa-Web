# Plataforma de Defensa Web en Tiempo de Ejecución

Base ejecutable previa al Sprint 1. Incluye modo simulado y real, infraestructura defensiva,
persistencia SQLite, correlación, política de bloqueo, clasificación e informes locales,
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

La API queda en `http://127.0.0.1:8000`; documentación OpenAPI en `/docs` y salud en
`/api/salud`.

## Verificación

```bash
make check-all
```

## Alcance actual

- `FakeSource` y `DryRunActuator` permiten desarrollar sin VM.
- `EveSource` y `Fail2banActuator` conectan Suricata y el firewall en modo real.
- Un evento se agrupa por IP y categoría dentro de una ventana configurable.
- Cinco eventos de severidad media o alta en 60 segundos producen un baneo simulado.
- La lista blanca y los baneos ya vigentes evitan acciones duplicadas.
- El enriquecedor genera la ficha con Ollama o plantilla y envía FCM para severidad alta.
- La app Android consume autenticación, incidentes, informes, bloqueos y liberación remota.

## Modo real

La infraestructura y el orden de despliegue están documentados en `infra/README.md`. El modo
real exige `DEFENSA_JWT_SECRET`, `DEFENSA_ADMIN_PASSWORD`, acceso a `eve.json` y el permiso
limitado de `sudoers` para `fail2ban-client`.
