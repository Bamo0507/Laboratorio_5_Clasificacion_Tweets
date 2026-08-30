"""
Funciones de analisis de sentimiento, reutilizables.
------------------------------------------------------------
Este modulo NO es una etapa del pipeline: es la libreria que usan la etapa 09
y el notebook de los ejercicios 8, 9 y 10.

Existe por la misma razon que texto.py. La logica de conteo de palabras vivia
duplicada, escrita una vez en la etapa y otra vez en el notebook, y las dos
versiones divergieron: la del pipeline no limpiaba la puntuacion antes de
buscar en el lexico, de tal forma que "amazing," no encontraba "amazing" y el
conteo salia corto en el 12.9% de los tweets. Al vivir aca, el pipeline y el
notebook llaman al mismo codigo y no pueden separarse.

Se trabaja sobre texto_sentimiento (la limpieza conservadora de texto.py) y no
sobre tokens, porque VADER necesita mayusculas, puntuacion y negaciones
intactas para poder funcionar.

Modulo externo usado: vaderSentiment, cuyo lexico y reglas estan hechos para
texto de redes sociales, a diferencia del lexico general de TextBlob.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Umbrales estandar de VADER para cortar el puntaje compuesto en tres clases.
UMBRAL_POSITIVO = 0.05
UMBRAL_NEGATIVO = -0.05

# Signos que se recortan del borde del token antes de buscarlo en el lexico.
# texto_sentimiento conserva la puntuacion a proposito, asi que sin este paso
# "amazing," no coincide con la entrada "amazing" del lexico.
SIGNOS_BORDE = ".,!?;:\"'()[]"

ANALIZADOR = SentimentIntensityAnalyzer()

# Columnas que produce puntuar_dataframe.
COLUMNAS = [
    "n_palabras_positivas",
    "n_palabras_negativas",
    "sentimiento_compound",
    "negatividad",
    "sentimiento_clase",
]


def contar_palabras(texto):
    """
    Cuenta cuantas palabras del tweet estan en el lexico de VADER con signo
    positivo y cuantas con signo negativo.

    Devuelve la tupla (positivas, negativas).
    """
    positivas = negativas = 0
    for token in str(texto).split():
        minuscula = token.lower()
        # Se busca primero el token tal cual, porque los emoticones estan en el
        # lexico con sus signos incluidos y recortarlos los destruiria: ":)" se
        # volveria ":". Solo si no aparece se prueba la version recortada.
        puntaje = ANALIZADOR.lexicon.get(minuscula)
        if puntaje is None:
            puntaje = ANALIZADOR.lexicon.get(minuscula.strip(SIGNOS_BORDE))
        if puntaje is None:
            continue
        if puntaje > 0:
            positivas += 1
        elif puntaje < 0:
            negativas += 1
    return positivas, negativas


def clasificar(compound):
    """Corta el puntaje compuesto en positivo, negativo o neutro."""
    if compound >= UMBRAL_POSITIVO:
        return "positivo"
    if compound <= UMBRAL_NEGATIVO:
        return "negativo"
    return "neutro"


def puntuar_tweet(tweet):
    """
    Recibe el texto de un tweet y devuelve su analisis de sentimiento completo.

    Es la funcion del ejercicio 8: reporta cuantas palabras positivas y
    negativas trae, el puntaje compuesto, la negatividad y la clase.
    """
    positivas, negativas = contar_palabras(tweet)
    puntajes = ANALIZADOR.polarity_scores(str(tweet))
    return {
        "tweet": tweet,
        "n_palabras_positivas": positivas,
        "n_palabras_negativas": negativas,
        "sentimiento_compound": round(puntajes["compound"], 4),
        "negatividad": round(puntajes["neg"], 4),
        "sentimiento_clase": clasificar(puntajes["compound"]),
    }


def puntuar_dataframe(df, columna="texto_sentimiento"):
    """Aplica puntuar_tweet a una columna y pega las cinco columnas resultantes."""
    puntuados = df[columna].map(puntuar_tweet)
    for nombre in COLUMNAS:
        df[nombre] = puntuados.map(lambda d, n=nombre: d[n])
    return df
