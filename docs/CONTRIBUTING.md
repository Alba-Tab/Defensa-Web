# Guía de contribución

## Flujo de trabajo

1. Crear una rama desde `main`: `feature/Pb-<n>-descripcion`, `fix/descripcion` o
   `docs/descripcion`.
2. Mantener cada cambio enfocado en una sola historia o corrección.
3. Ejecutar `make check` antes de abrir un pull request.
4. Integrar mediante pull request aprobado; no hacer push directo a `main`.

## Commits y versiones

Los commits usan Conventional Commits:

- `feat(backend): agrega correlacion de eventos`
- `fix(politicas): evita duplicar un bloqueo vigente`
- `test(correlador): cubre vencimiento de ventana`
- `docs: actualiza instrucciones de desarrollo`

La versión pública usa SemVer (`MAJOR.MINOR.PATCH`). Los cambios incompatibles incrementan
MAJOR, funcionalidad compatible MINOR y correcciones PATCH.

## Estándares

- Python 3.12 o superior, anotaciones de tipos y nombres en español coherentes con el dominio.
- Ruff para lint y formato; mypy para tipos; pytest para pruebas.
- No incluir secretos, tokens, datos capturados ni archivos `.env`.
- Las fechas persistidas son UTC.
- Las acciones externas se abstraen detrás de interfaces y nunca usan `shell=True`.
