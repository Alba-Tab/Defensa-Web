# Entrenamiento de IA local

El clasificador usa TF-IDF de n-gramas de caracteres y regresión logística. Los datos no se
versionan; deben seguir el esquema de `captura/esquema.csv` y documentar origen y licencia.

```bash
source .venv/bin/activate
python ia/entrenamiento/entrenar.py \
  --entrada ia/datos/peticiones.csv \
  --salida servicio/modelos/clasificador.joblib \
  --reporte ia/resultados/evaluacion.json
```

El servicio carga el artefacto mediante `DEFENSA_MODELO_CLASIFICADOR`. Si no existe, utiliza
`ClasificadorNulo` y mantiene la severidad de la firma.
