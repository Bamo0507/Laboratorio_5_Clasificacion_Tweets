"""
Etapa 9 del pipeline: ANALISIS DE SENTIMIENTO
------------------------------------------------------------
Una sola responsabilidad: puntuar el sentimiento de cada tweet y dejar la
variable de "negatividad" pegada a train/test para el ejercicio 10.

  Lee : data/processed/train_modelado.csv
        data/processed/test_modelado.csv
  Hace: - cuenta palabras positivas/negativas segun el lexico de VADER
        - calcula el puntaje compuesto de VADER y clasifica en
          positivo / negativo / neutro
        - deriva "negatividad" (componente "neg" de VADER, en [0, 1])
  Escribe: los mismos train_modelado.csv / test_modelado.csv, con columnas nuevas

Se usa la columna `texto_sentimiento` (limpieza conservadora de texto.py) y no
`tokens`, porque VADER necesita mayusculas, puntuacion y negaciones intactas
para funcionar. Ver texto.py, normalizar_para_sentimiento.

Se descarto conservar emoticones ASCII: decisiones.md ya midio que aparecen en
menos del 1% de los tweets, asi que no habria como moverle el resultado.

Modulo externo usado: vaderSentiment (lexico + regla compuesta pensados para
texto de redes sociales, a diferencia del lexico general de TextBlob).

Ejecutar:  python src/09_sentimiento.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import config
from utils import afirmar, afirmar_columnas, banner, cargar, guardar

UMBRAL_POSITIVO = 0.05
UMBRAL_NEGATIVO = -0.05

analizador = SentimentIntensityAnalyzer()


def clasificar(compound):
    if compound >= UMBRAL_POSITIVO:
        return "positivo"
    if compound <= UMBRAL_NEGATIVO:
        return "negativo"
    return "neutro"


def contar_palabras(texto):
    """Cuenta cuantos tokens del tweet estan en el lexico de VADER con signo positivo/negativo."""
    positivas = negativas = 0
    for token in str(texto).split():
        puntaje = analizador.lexicon.get(token.lower())
        if puntaje is None:
            continue
        if puntaje > 0:
            positivas += 1
        elif puntaje < 0:
            negativas += 1
    return positivas, negativas


def puntuar(df):
    conteos = df["texto_sentimiento"].apply(contar_palabras)
    df["n_palabras_positivas"] = conteos.apply(lambda t: t[0])
    df["n_palabras_negativas"] = conteos.apply(lambda t: t[1])

    puntajes = df["texto_sentimiento"].apply(analizador.polarity_scores)
    df["sentimiento_compound"] = puntajes.apply(lambda d: d["compound"])
    df["negatividad"] = puntajes.apply(lambda d: d["neg"])
    df["sentimiento_clase"] = df["sentimiento_compound"].apply(clasificar)
    return df


banner("Etapa 9: analisis de sentimiento")

train = cargar(config.RUTA_TRAIN)
test = cargar(config.RUTA_TEST)
afirmar_columnas(train, ["texto_sentimiento", "target"], "contrato de la etapa 08")

train = puntuar(train)
test = puntuar(test)

afirmar(train["negatividad"].between(0, 1).all(), "negatividad queda en el rango [0, 1]")
afirmar(set(train["sentimiento_clase"]) <= {"positivo", "negativo", "neutro"},
        "la clasificacion de sentimiento solo usa las tres etiquetas esperadas")

print(f"[ok]       distribucion de sentimiento (train): "
      f"{train['sentimiento_clase'].value_counts().to_dict()}")

guardar(train, config.RUTA_TRAIN)
guardar(test, config.RUTA_TEST)
