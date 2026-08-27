"""
Etapa 1 del pipeline: INGESTA
------------------------------------------------------------
Una sola responsabilidad: cargar el crudo tal cual viene y verificar que
cumple el contrato minimo antes de que cualquier otra etapa lo toque.

  Lee : data/raw/train.csv
  Hace: - carga todo como texto (dtype=str) para no dejar que pandas
          infiera tipos antes de tiempo
        - valida que esten las 5 columnas esperadas
        - valida que id sea unico y que target solo tenga 0 y 1
  Escribe: data/processed/01_ingesta.csv

Ejecutar:  python src/01_ingesta.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from utils import afirmar, afirmar_columnas, banner, cargar, guardar

# Valores que el crudo usa para marcar ausencia. Se dejan como NaN, no se imputan.
ETIQUETAS_VALIDAS = {"0", "1"}


def main():
    banner("Etapa 1: ingesta del archivo crudo")

    # dtype=str a proposito: el texto de los tweets debe llegar intacto a la
    # etapa que le toca, sin que pandas convierta nada por su cuenta.
    df = cargar(config.RUTA_CRUDA, dtype=str)

    afirmar_columnas(df, config.COLUMNAS_CRUDAS, "crudo")
    afirmar(len(df) == config.FILAS_CRUDAS_ESPERADAS,
            f"el crudo trae las {config.FILAS_CRUDAS_ESPERADAS:,} filas esperadas (trae {len(df):,})")
    afirmar(df["id"].notna().all() and not df["id"].duplicated().any(),
            "id esta completo y sin duplicados")
    afirmar(df["text"].notna().all(), "text no tiene faltantes")
    afirmar(set(df["target"].dropna().unique()) <= ETIQUETAS_VALIDAS,
            "target solo contiene los valores 0 y 1")

    # Se conserva el orden de columnas del contrato.
    df = df[config.COLUMNAS_CRUDAS]

    print(f"[ok]       faltantes por columna: {df.isna().sum().to_dict()}")
    guardar(df, config.RUTA_INGESTA)


main()
