# Plataforma de Defensa Web en Tiempo de Ejecución

Base ejecutable previa al Sprint 1. Incluye el servicio de defensa en modo simulado,
persistencia SQLite, migraciones, correlación de eventos y política de bloqueo con un
actuador que no modifica el firewall.

## Requisitos

- Python 3.12+
- Docker y Docker Compose (opcional)

## Desarrollo local

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e './servicio[dev]'
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
make check
```

## Alcance actual

- `FakeSource` y `DryRunActuator` permiten desarrollar sin VM.
- Un evento se agrupa por IP y categoría dentro de una ventana configurable.
- Cinco eventos de severidad media o alta en 60 segundos producen un baneo simulado.
- La lista blanca y los baneos ya vigentes evitan acciones duplicadas.
- La integración real con Suricata, Fail2ban, nftables y la app móvil queda fuera de esta base.
