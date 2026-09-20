# Dependencias web locales

Estos archivos se sirven desde `/static/vendor/`; el panel no depende de CDN ni de internet.

| Archivo | Paquete | Versión | Licencia | Origen |
|---|---|---:|---|---|
| `htmx.min.js` | htmx | 2.0.10 | 0BSD | `unpkg.com/htmx.org@2.0.10/dist/htmx.min.js` |
| `alpine.min.js` | Alpine.js | 3.17.3 | MIT | `cdn.jsdelivr.net/npm/alpinejs@3.17.3/dist/cdn.min.js` |
| `chart.umd.js` | Chart.js | 4.5.1 | MIT | `cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.js` |

Las versiones son deliberadamente exactas para que el artefacto sea reproducible.
