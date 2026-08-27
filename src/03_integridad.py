"""
Etapa 3 del pipeline: INTEGRIDAD DE LAS FILAS
------------------------------------------------------------
Una sola responsabilidad: dejar una fila por tweet, con etiqueta confiable
y tipos correctos.

  Lee : data/processed/02_codificacion.csv
  Hace: - descarta los textos con etiquetas contradictorias (mismo texto
          marcado como desastre y como no desastre)
        - deduplica los textos repetidos, conservando la primera aparicion
        - tipa id y target a entero
  Escribe: data/processed/03_integridad.csv

Por que se eliminan filas aca, si la politica del curso dice no borrar por
NaN: no se borra por faltantes, se borra por violar una regla dura. Un texto
con dos etiquetas distintas no puede ser correcto en ambos casos, y un
duplicado que caiga repartido entre entrenamiento y prueba infla la metrica
de prueba porque el modelo lo memoriza (fuga de datos).

El EDA (seccion 2.5) conto 110 textos duplicados y 18 con etiquetas
contradictorias.

Ejecutar:  python src/03_integridad.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from utils import afirmar, afirmar_columnas, banner, cargar, guardar


def main():
    banner("Etapa 3: integridad de las filas")

    df = cargar(config.RUTA_CODIFICACION, dtype=str)
    afirmar_columnas(df, config.COLUMNAS_CRUDAS, "contrato de la etapa 02")

    filas_iniciales = len(df)

    # 1) Textos con mas de una etiqueta distinta: no hay forma de saber cual
    #    es la correcta, asi que se descartan todas sus apariciones en lugar
    #    de elegir una al azar.
    etiquetas_por_texto = df.groupby("text")["target"].nunique()
    contradictorios = etiquetas_por_texto[etiquetas_por_texto > 1].index
    df = df[~df["text"].isin(contradictorios)]
    print(f"[ok]       descartados {len(contradictorios)} textos contradictorios "
          f"({filas_iniciales - len(df)} filas)")

    # 2) Duplicados exactos: se conserva la primera aparicion.
    filas_previas = len(df)
    df = df.drop_duplicates(subset="text", keep="first")
    print(f"[ok]       eliminados {filas_previas - len(df)} duplicados de text")

    # 3) Tipado. Se hace aca y no antes porque las etapas 01 y 02 necesitan
    #    el texto crudo intacto.
    df["id"] = df["id"].astype(int)
    df["target"] = df["target"].astype(int)

    afirmar(not df["text"].duplicated().any(), "no queda ningun texto duplicado")
    afirmar(df.groupby("text")["target"].nunique().max() == 1,
            "cada texto tiene una sola etiqueta")
    afirmar(set(df["target"].unique()) <= config.TARGET_VALIDOS,
            "target sigue siendo binaria (0/1)")
    afirmar(not df["id"].duplicated().any(), "id sigue siendo unico")

    tasa = df["target"].mean()
    print(f"[ok]       filas: {filas_iniciales:,} -> {len(df):,} "
          f"({filas_iniciales - len(df)} descartadas) | tasa de desastre: {tasa:.4f}")

    guardar(df, config.RUTA_INTEGRIDAD)


main()
