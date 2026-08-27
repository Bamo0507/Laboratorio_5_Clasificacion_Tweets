"""
Etapa 6 del pipeline: TOKENIZACION
------------------------------------------------------------
Una sola responsabilidad: convertir texto_limpio en la lista de tokens que
consume el ejercicio 4 (n-gramas) y el ejercicio 6 (modelos).

  Lee : data/processed/05_texto_limpio.csv
  Hace: - quita los tokens que son solo numeros, salvo el token de emergencia
        - quita las stopwords en ingles (corpus de NLTK)
        - quita los tokens de menos de 3 caracteres
        - lematiza con WordNet para unificar fires/fire
  Escribe: data/processed/tweets_procesado.csv   <- dataset final del ejercicio 3

Modulos externos usados: NLTK (corpus stopwords y wordnet). Se descargan
corriendo python src/00_init.py.

Ejecutar:  python src/06_tokenizacion.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
import texto as tx
from utils import afirmar, afirmar_columnas, banner, cargar, guardar

IDIOMA_STOPWORDS = "english"
MINIMO_CARACTERES = 3


def cargar_recursos_nltk():
    """Devuelve el set de stopwords y el lematizador, o corta con un mensaje util."""
    try:
        from nltk.corpus import stopwords, wordnet
        from nltk.stem import WordNetLemmatizer

        palabras = set(stopwords.words(IDIOMA_STOPWORDS))
        lematizador = WordNetLemmatizer()
        wordnet.ensure_loaded()
    except LookupError as error:
        print("[FALLO]    faltan los corpus de NLTK. Corra: python src/00_init.py")
        print(f"           detalle: {error.args[0].splitlines()[0] if error.args else error}")
        sys.exit(1)

    print(f"[ok]       stopwords cargadas: {len(palabras)} palabras en {IDIOMA_STOPWORDS}")
    return palabras, lematizador


def main():
    banner("Etapa 6: tokenizacion")

    df = cargar(config.RUTA_TEXTO)
    afirmar_columnas(df, config.COLUMNAS_TEXTO, "contrato de la etapa 05")

    palabras_vacias, lematizador = cargar_recursos_nltk()

    listas = df["texto_limpio"].map(
        lambda t: tx.tokenizar(t, palabras_vacias, lematizador, MINIMO_CARACTERES)
    )
    df[config.COLUMNA_TOKENS] = listas.map(" ".join)
    df["n_tokens"] = listas.map(len)

    sin_tokens = (df["n_tokens"] == 0).sum()
    vocabulario = {token for lista in listas for token in lista}

    afirmar(config.COLUMNA_TOKENS in df.columns, "existe la columna tokens")
    afirmar(not df[config.COLUMNA_TOKENS].str.contains(r"\b\d+\b", regex=True).any(),
            "no quedo ningun token puramente numerico")
    afirmar(not any(t in palabras_vacias for t in vocabulario),
            "no quedo ninguna stopword en el vocabulario")
    afirmar(tx.TOKEN_EMERGENCIA in vocabulario,
            f"el token {tx.TOKEN_EMERGENCIA} sigue en el vocabulario")
    afirmar(len(df) > 0, "el dataset final no quedo vacio")

    print(f"[ok]       vocabulario final: {len(vocabulario):,} terminos distintos")
    print(f"[ok]       tokens por tweet: media {df['n_tokens'].mean():.2f} | "
          f"minimo {df['n_tokens'].min()} | maximo {df['n_tokens'].max()}")
    print(f"[ok]       tweets que quedaron sin ningun token: {sin_tokens}")

    guardar(df, config.RUTA_FINAL)


main()
