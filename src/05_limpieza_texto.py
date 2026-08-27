"""
Etapa 5 del pipeline: NORMALIZACION DEL TEXTO
------------------------------------------------------------
Una sola responsabilidad: producir las dos versiones normalizadas del texto.

  Lee : data/processed/04_features_crudas.csv
  Hace: - texto_limpio: version agresiva (sin URLs, menciones, simbolos,
          puntuacion ni mayusculas) que alimenta n-gramas y modelos
        - texto_sentimiento: version conservadora que mantiene puntuacion,
          mayusculas y negaciones, y alimenta el analisis de sentimiento
  Escribe: data/processed/05_texto_limpio.csv

Son dos columnas y no una porque el preprocesamiento que necesita el
clasificador destruye lo que el analisis de sentimiento necesita leer.
La logica vive en texto.py para que el ejercicio 7 pueda reutilizarla.

Ejecutar:  python src/05_limpieza_texto.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
import texto as tx
from utils import afirmar, afirmar_columnas, banner, cargar, guardar


def main():
    banner("Etapa 5: normalizacion del texto")

    df = cargar(config.RUTA_FEATURES)
    afirmar_columnas(df, config.COLUMNAS_CRUDAS + config.COLUMNAS_FEATURES,
                     "contrato de la etapa 04")

    df["texto_limpio"] = df["text"].map(tx.normalizar_para_modelo)
    df["texto_sentimiento"] = df["text"].map(tx.normalizar_para_sentimiento)

    vacios = (df["texto_limpio"].str.len() == 0).sum()
    con_token = df["texto_limpio"].str.contains(tx.TOKEN_EMERGENCIA).sum()

    afirmar_columnas(df, config.COLUMNAS_TEXTO, "salida de la etapa 05")
    afirmar(df["texto_limpio"].notna().all() and df["texto_sentimiento"].notna().all(),
            "ninguna de las dos versiones quedo nula")
    afirmar(not df["texto_limpio"].str.contains(r"https?://", regex=True).any(),
            "no quedan URLs en texto_limpio")
    afirmar(not df["texto_limpio"].str.contains("@", regex=False).any(),
            "no quedan menciones en texto_limpio")
    afirmar(not df["texto_limpio"].str.contains(r"[^a-z0-9\s]", regex=True).any(),
            "texto_limpio solo tiene minusculas, digitos y espacios")
    afirmar(con_token > 0, f"el token {tx.TOKEN_EMERGENCIA} sobrevivio en {con_token} tweets")

    print(f"[ok]       tweets que quedaron sin texto tras limpiar: {vacios}")
    print("[ok]       ejemplo de las dos versiones:")
    fila = df.iloc[1]
    print(f"             crudo      : {fila['text'][:90]!r}")
    print(f"             limpio     : {fila['texto_limpio'][:90]!r}")
    print(f"             sentimiento: {fila['texto_sentimiento'][:90]!r}")

    guardar(df, config.RUTA_TEXTO)


main()
