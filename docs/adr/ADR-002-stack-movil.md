# ADR-002: Mantener el stack móvil ligero del MVP

**Estado:** Aceptada
**Fecha:** 2026-09-19
**Decisores:** Equipo del proyecto

## Contexto

C-35 proponía Riverpod y `go_router`, pero la aplicación funcional ya usa Dio,
`flutter_secure_storage`, estado local y `Navigator`. Migrar el stack completo no añade valor a las
historias del primer parcial y elevaría el riesgo sobre autenticación, detalle y liberación de
bloqueos.

## Decisión

Se mantienen Dio, almacenamiento seguro, `StatefulWidget` y Navigator de Flutter. Las rutas de
primer nivel se registran por nombre en `MaterialApp`; `/configuracion` es una ruta real y accesible
desde Inicio. Incidentes y bloqueos permanecen unidos en Inicio porque forman un único flujo
operativo del MVP.

## Opciones consideradas

| Opción | Complejidad | Beneficio inmediato | Riesgo |
|---|---:|---:|---:|
| Mantener stack actual | Baja | Alto | Bajo |
| Migrar a Riverpod + go_router | Alta | Bajo en este alcance | Medio |

## Consecuencias

- Se cumplen las cinco capacidades de navegación: login, incidentes, detalle, bloqueos y
  configuración, aunque incidentes/bloqueos compartan pantalla.
- No existe dependencia adicional de estado o enrutamiento.
- Si la app crece, se reevaluará `go_router` para enlaces profundos y Riverpod para estado global.
