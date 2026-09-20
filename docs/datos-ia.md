# Decisión de datos para el clasificador local

**Fecha de verificación:** 2026-09-19
**Decisión:** no incorporar HTTP CSIC 2010; usar captura propia etiquetada del laboratorio.

## Verificación de HTTP CSIC 2010

La URL original publicada para el conjunto (`http://www.isi.csic.es/dataset/`) ya no es accesible.
El catálogo de IMPACT conserva el registro DS-0940 y el DOI `10.23721/100/1478804`, pero lo declara
como recurso externo: IMPACT no controla su disponibilidad ni sus términos. El registro marca
acceso “Unrestricted”, deja “Commercial Allowed” como desconocido y no muestra términos de uso.

Referencias consultadas:

- Registro preservado: https://www.impactcybertrust.org/dataset_view?idDataset=940
- DOI del registro: https://doi.org/10.23721/100/1478804
- Fuente original no disponible: http://www.isi.csic.es/dataset/

Los espejos encontrados no aportan una licencia emitida por CSIC para los archivos del dataset.
Por ello, descargarlos e incorporarlos al proyecto dejaría abierta la procedencia y el permiso de
redistribución. El estado “Unrestricted” del catálogo no sustituye una licencia del titular.

## Fuente adoptada

Se usarán exclusivamente peticiones generadas contra la VM de laboratorio y etiquetadas por una
ventana en la que se ejecuta una sola fuente:

| Etiqueta | Fuente |
|---|---|
| `benigno` | Navegación manual y k6 sobre rutas normales |
| `sqli` | sqlmap y payloads SQLi controlados |
| `xss` | curl/ZAP con payloads XSS controlados |
| `traversal` | curl/ZAP con rutas de traversal controladas |
| `escaneo` | Nikto y ffuf con tasa moderada |
| `fuerza_bruta` | Guion local con pocas credenciales de prueba |

Cada captura debe conservar fecha UTC, herramienta, versión, comando, objetivo autorizado y rango
horario. Los datos crudos viven en `ia/datos/` (ignorado por Git). Solo se versiona la muestra
sintética pequeña de `ia/muestras/`, que permite verificar el pipeline y no representa métricas de
calidad del modelo final.

## Revisión de la decisión

Se puede reconsiderar CSIC 2010 si aparece una fuente oficial accesible con licencia explícita y
condiciones de citación. Hasta entonces, la evaluación del modelo debe declarar que usa datos
propios y que la muestra sintética solo prueba la cadena técnica.

## Meta inicial de evaluación

Tras la primera evaluación se fija para la clase `sqli` una precisión y una exhaustividad mínimas
de 0,80 sobre el conjunto de prueba. La muestra versionada solo valida la cadena técnica; antes de
una demostración de calidad se debe repetir la evaluación con captura propia independiente.
