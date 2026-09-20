# Evidencia de ejecución del pipeline

El 2026-09-19 se ejecutó, desde la raíz del repositorio:

```bash
.venv/bin/python ia/entrenamiento/entrenar.py \
  --entrada ia/muestras/peticiones_demo.csv \
  --salida servicio/modelos/clasificador.joblib \
  --reporte ia/resultados/evaluacion_demo.json
```

Entorno observado: Python 3.14.7, scikit-learn 1.9.1, joblib 1.6.0 y pandas 3.0.6. El resultado
usó 24 filas para entrenamiento y 6 para prueba, exportó el artefacto y produjo la matriz de
confusión. Después, `ClasificadorJoblib` —el adaptador usado por el backend— cargó el archivo y
ejecutó `predict_proba` sobre una petición SQLi sin acceso a red.

SHA-256:

```text
aa17ddd5123e43c2077ffadf4318a1401f5e6c01619af51d7743ee2f7ecc9aaa  servicio/modelos/clasificador.joblib
aff545fbc35d1fbc7be3b2d979d1441966b78bb0bf15abcece40480bd20ff941  ia/muestras/peticiones_demo.csv
1a3355783158e17da7ac3f6cb043321088910a2461a3703595cf79fcf6df2b6b  ia/resultados/evaluacion_demo.json
```

La exactitud 5/6 de esta muestra no es una medición válida para producción: cada clase tiene una
sola fila de prueba. Esta ejecución demuestra reproducibilidad, exportación y carga; la evaluación
de Pb-20 debe repetirse con la captura propia descrita en `docs/datos-ia.md`.

**Nota posterior:** la carpeta `servicio/` se renombró a `backend/` después de esta ejecución. El
comando, la ruta de salida y los hashes de arriba quedan tal como se registraron ese día (el
archivo es el mismo, solo cambió su ubicación); el artefacto vigente está en
`backend/modelos/clasificador.joblib`.
