"""
Etapa 7 del pipeline: VARIANTE CON STEMMING
------------------------------------------------------------
Una sola responsabilidad: producir la version de los tokens reducida con
stemming, para poder comparar los dos enfoques en el ejercicio 6.

  Lee : data/processed/tweets_procesado.csv
  Hace: - aplica el stemmer de Snowball sobre texto_limpio
        - deja la columna tokens_stem junto a la tokens ya lematizada
  Escribe: data/processed/07_stemming.csv

La lematizacion devuelve una palabra real (fires -> fire) mientras que el
stemming corta la palabra a su raiz aunque no exista (fires -> fire, pero
tambien disaster -> disast). Cual funciona mejor depende del corpus, y por
eso no se elige de antemano: se generan las dos y se comparan midiendo.

Modulo externo usado: NLTK (SnowballStemmer).

Ejecutar:  python src/07_stemming.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
import texto as tx
from utils import afirmar, afirmar_columnas, banner, cargar, guardar

IDIOMA = "english"
MINIMO_CARACTERES = 3


def cargar_recursos():
    from nltk.corpus import stopwords
    from nltk.stem import SnowballStemmer

    return set(stopwords.words(IDIOMA)), SnowballStemmer(IDIOMA)


banner("Etapa 7: variante con stemming")

df = cargar(config.RUTA_FINAL)
afirmar_columnas(df, ["texto_limpio", config.COLUMNA_TOKENS], "contrato de la etapa 06")

palabras_vacias, stemmer = cargar_recursos()

listas = df["texto_limpio"].map(
    lambda t: tx.tokenizar(t, palabras_vacias, stemmer.stem, MINIMO_CARACTERES)
)
df[config.COLUMNA_TOKENS_STEM] = listas.map(" ".join)

vocab_stem = {t for lista in listas for t in lista}
vocab_lema = {t for s in df[config.COLUMNA_TOKENS].fillna("") for t in s.split()}

afirmar_columnas(df, [config.COLUMNA_TOKENS_STEM], "salida de la etapa 07")
afirmar(not df[config.COLUMNA_TOKENS_STEM].str.contains(r"\b\d+\b", regex=True).any(),
        "no quedo ningun token puramente numerico")
afirmar(tx.TOKEN_EMERGENCIA in vocab_stem,
        f"el token {tx.TOKEN_EMERGENCIA} sobrevivio al stemming")
afirmar(len(vocab_stem) < len(vocab_lema),
        f"el stemming comprime mas que la lematizacion "
        f"({len(vocab_stem):,} vs {len(vocab_lema):,} terminos)")

print(f"[ok]       vocabulario con lematizacion: {len(vocab_lema):,} terminos")
print(f"[ok]       vocabulario con stemming    : {len(vocab_stem):,} terminos "
      f"({(1 - len(vocab_stem) / len(vocab_lema)) * 100:.1f}% mas compacto)")
print("[ok]       ejemplo de las dos variantes:")
fila = df.iloc[1]
print(f"             lematizado: {fila[config.COLUMNA_TOKENS]!r}")
print(f"             stemming  : {fila[config.COLUMNA_TOKENS_STEM]!r}")

guardar(df, config.RUTA_STEMMING)
