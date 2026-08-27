"""
Etapa 4 del pipeline: EXTRACCION DE SENAL DEL TEXTO CRUDO
------------------------------------------------------------
Una sola responsabilidad: medir sobre el texto todavia sin limpiar las
caracteristicas que la limpieza va a destruir.

  Lee : data/processed/03_integridad.csv
  Hace: - tiene_url, n_hashtags, n_menciones
        - n_caracteres, n_palabras
        - n_mayusculas
  Escribe: data/processed/04_features_crudas.csv

Por que esta etapa va ANTES de la limpieza: el EDA (seccion 2.6) encontro que
entre los tweets sin URL solo el 30% son desastre real, contra un 55% entre
los que si la traen. Esa es la senal auxiliar mas fuerte del dataset, y la
etapa 05 borra las URLs. La cadena de la URL no sirve como token, pero el
hecho de que existiera si informa: se elimina la cadena y se conserva la senal.

Lo mismo aplica a las mayusculas, que el paso a minusculas de la etapa 05
elimina sin dejar rastro.

Ejecutar:  python src/04_features_crudas.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from utils import afirmar, afirmar_columnas, banner, cargar, guardar

# Patrones medidos en el EDA, seccion 2.4.
PATRON_URL = r"https?://\S+"
PATRON_HASHTAG = r"#\w+"
PATRON_MENCION = r"@\w+"
PATRON_MAYUSCULAS = r"\b[A-Z]{3,}\b"


def main():
    banner("Etapa 4: extraccion de senal del texto crudo")

    df = cargar(config.RUTA_INTEGRIDAD)
    afirmar_columnas(df, config.COLUMNAS_CRUDAS, "contrato de la etapa 03")

    texto = df["text"]
    df["tiene_url"] = texto.str.contains(PATRON_URL, regex=True, na=False).astype(int)
    df["n_hashtags"] = texto.str.count(PATRON_HASHTAG)
    df["n_menciones"] = texto.str.count(PATRON_MENCION)
    df["n_caracteres"] = texto.str.len()
    df["n_palabras"] = texto.str.split().str.len()
    df["n_mayusculas"] = texto.str.count(PATRON_MAYUSCULAS)

    afirmar_columnas(df, config.COLUMNAS_FEATURES, "salida de la etapa 04")
    afirmar(df[config.COLUMNAS_FEATURES].notna().all().all(),
            "ninguna variable derivada quedo con faltantes")
    afirmar((df[config.COLUMNAS_FEATURES] >= 0).all().all(),
            "todos los conteos son no negativos")
    afirmar(df["tiene_url"].isin([0, 1]).all(), "tiene_url es binaria")

    print("[ok]       medias por clase:")
    print(df.groupby("target")[config.COLUMNAS_FEATURES].mean().round(3).to_string())

    guardar(df, config.RUTA_FEATURES)


main()
