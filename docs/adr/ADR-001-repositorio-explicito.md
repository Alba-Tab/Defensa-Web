# ADR-001: Capa de repositorio explícita

**Estado:** Aceptada
**Fecha:** 2026-09-19
**Decisores:** Equipo del proyecto

## Contexto

C-27 exige una capa `Repositorio`, transacciones cortas y una prueba de escrituras concurrentes.
El código inicial abría sesiones directamente desde servicios y endpoints, por lo que la frontera de
persistencia no era visible como componente C4 y no existía una prueba específica de concurrencia.

## Decisión

Se crea `servicio/app/repositorio.py`. Cada método abre y cierra su propia sesión; la unidad de
trabajo común está en `Repositorio.transaccion()`. El conciliador usa esta capa y las nuevas
operaciones de persistencia deben agregarse allí. Los endpoints heredados migrarán gradualmente,
sin reescribir en bloque código que ya está cubierto por pruebas.

SQLite se configura con WAL, `synchronous=NORMAL`, claves foráneas y `busy_timeout=5000`. La prueba
de aceptación escribe 200 eventos desde ocho hilos y verifica el total.

## Opciones consideradas

### A. Repositorio explícito

| Dimensión | Evaluación |
|---|---|
| Complejidad | Media |
| Riesgo de concurrencia | Bajo, con sesiones breves y prueba dedicada |
| Trazabilidad con C-27 | Directa |
| Migración | Gradual |

### B. Declarar `servicios.py` como persistencia

| Dimensión | Evaluación |
|---|---|
| Complejidad inicial | Baja |
| Riesgo de concurrencia | Medio; mezcla negocio y unidad de trabajo |
| Trazabilidad con C-27 | Indirecta y divergente del diseño aprobado |
| Migración | Ninguna |

## Consecuencias

- C-23 y C-27 tienen componentes concretos y comprobables.
- El ciclo de vida de las sesiones queda centralizado para código nuevo.
- Temporalmente conviven endpoints con sesiones inyectadas y operaciones del repositorio.
- No se esconde SQLModel: las consultas continúan tipadas y revisables.

## Acciones

- [x] Crear `Repositorio` y usarlo desde `Conciliador`.
- [x] Configurar espera de bloqueos SQLite.
- [x] Añadir prueba concurrente.
- [ ] Migrar endpoints al repositorio cuando cambien por una historia funcional.
