import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

CAMPOS = (
    "metodo",
    "uri_decodificada",
    "parametros",
    "cuerpo_fragmento",
    "user_agent",
    "categoria_firma",
)


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Entrena el clasificador HTTP local")
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--reporte", type=Path, required=True)
    return parser.parse_args()


def texto_por_fila(datos: pd.DataFrame) -> pd.Series:
    faltantes = {*CAMPOS, "etiqueta"} - set(datos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas: {', '.join(sorted(faltantes))}")
    return datos.loc[:, CAMPOS].fillna("").astype(str).agg(" ".join, axis=1)


def entrenar(entrada: Path, salida: Path, reporte: Path) -> None:
    datos = pd.read_csv(entrada)
    textos = texto_por_fila(datos)
    etiquetas = datos["etiqueta"].astype(str)
    if etiquetas.nunique() < 2:
        raise ValueError("Se necesitan al menos dos clases para entrenar")
    if etiquetas.value_counts().min() < 2:
        raise ValueError("Cada clase necesita al menos dos ejemplos")

    x_entrena, x_prueba, y_entrena, y_prueba = train_test_split(
        textos,
        etiquetas,
        test_size=0.2,
        random_state=13,
        stratify=etiquetas,
    )
    modelo = Pipeline(
        [
            ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=1)),
            (
                "clasificador",
                LogisticRegression(
                    C=10,
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=13,
                ),
            ),
        ]
    )
    modelo.fit(x_entrena, y_entrena)
    prediccion = modelo.predict(x_prueba)
    evaluacion = {
        "muestras_entrenamiento": len(x_entrena),
        "muestras_prueba": len(x_prueba),
        "clases": sorted(etiquetas.unique().tolist()),
        "reporte": classification_report(
            y_prueba, prediccion, output_dict=True, zero_division=0
        ),
        "matriz_confusion": confusion_matrix(
            y_prueba, prediccion, labels=modelo.classes_
        ).tolist(),
    }

    salida.parent.mkdir(parents=True, exist_ok=True)
    reporte.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, salida)
    reporte.write_text(
        json.dumps(evaluacion, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    args = argumentos()
    entrenar(args.entrada, args.salida, args.reporte)
