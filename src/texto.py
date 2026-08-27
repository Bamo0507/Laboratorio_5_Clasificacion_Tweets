"""
Funciones de limpieza y tokenizacion de texto, reutilizables.
------------------------------------------------------------
Este modulo NO es una etapa del pipeline: es la libreria de transformaciones
que usan las etapas 05 y 06.

Existe por una razon concreta. El ejercicio 7 pide una funcion que reciba un
tweet crudo, sin preprocesar, y lo clasifique. Esa funcion tiene que aplicar
exactamente la misma limpieza con la que se entreno el modelo, y si la
limpieza viviera copiada dentro de los scripts de etapa terminaria divergiendo,
de tal forma que la funcion clasificaria distinto que el modelo evaluado.

Al vivir aca, el pipeline y el clasificador del ejercicio 7 llaman al mismo
codigo. Se separa en modulo propio porque los archivos de etapa empiezan con
digito (05_..., 06_...) y Python no permite importarlos.

Las decisiones que implementa cada funcion estan medidas en notebooks/analisis_pre.ipynb.
"""

import re

# ------------------------------------------------------------------ constantes de dominio

# Variantes con las que aparece el 11 de septiembre en el dataset. Se normalizan
# a un token unico ANTES de quitar puntuacion, porque si no la secuencia habitual
# lo destruye en dos pasos: quitar puntuacion parte 9/11 en "9" y "11", y quitar
# numeros borra los dos. Ver notebooks/analisis_pre.ipynb, seccion 2.4.
TOKEN_EMERGENCIA = "emergencia911"
PATRON_EMERGENCIA = re.compile(r"\b(?:911|9/11|9-11|wtc)\b", re.IGNORECASE)

PATRON_URL = re.compile(r"https?://\S+|www\.\S+")
PATRON_MENCION = re.compile(r"@\w+")
PATRON_RETWEET = re.compile(r"^RT\b[:\s]*", re.IGNORECASE)
PATRON_ESPACIOS = re.compile(r"\s+")
PATRON_NO_ASCII = re.compile(r"[^\x00-\x7F]")
# Incluye el guion bajo a proposito: \w lo considera caracter de palabra, pero en
# los handles y hashtags une palabras reales (our_mother_mary), asi que se separa.
PATRON_PUNTUACION = re.compile(r"[^\w\s]|_")
PATRON_TOKEN_NUMERICO = re.compile(r"^\d+$")

# Contracciones frecuentes en ingles. Se expanden antes de quitar la puntuacion
# porque, si no, el apostrofe parte la palabra y aparece el token basura "s"
# (ver notebooks/analisis_pre.ipynb, seccion 2.4, stopwords).
CONTRACCIONES = {
    "won't": "will not", "can't": "cannot", "n't": " not",
    "'re": " are", "'s": " is", "'d": " would",
    "'ll": " will", "'ve": " have", "'m": " am",
}
APOSTROFES = "‘’´`"


def _unificar_apostrofes(texto):
    """Lleva los apostrofes curvos al apostrofe recto para poder tratarlos igual."""
    for signo in APOSTROFES:
        texto = texto.replace(signo, "'")
    return texto


def _expandir_contracciones(texto):
    """don't -> do not. Lo que no este en la tabla pierde el apostrofe y se une."""
    for contraccion, expansion in CONTRACCIONES.items():
        texto = texto.replace(contraccion, expansion)
    return texto.replace("'", "")


def normalizar_para_modelo(texto):
    """
    Version agresiva del texto: la que alimenta los n-gramas y los modelos.

    El orden de los pasos no es intercambiable. La normalizacion del 911 va
    primero porque los pasos posteriores la destruirian, y el paso a minusculas
    va despues de contar mayusculas en la etapa 04.
    """
    if not isinstance(texto, str):
        return ""

    texto = PATRON_EMERGENCIA.sub(f" {TOKEN_EMERGENCIA} ", texto)
    texto = PATRON_URL.sub(" ", texto)
    texto = PATRON_RETWEET.sub(" ", texto)
    texto = PATRON_MENCION.sub(" ", texto)
    texto = texto.replace("#", " ")          # se quita el simbolo, se conserva la palabra
    texto = texto.lower()
    texto = _unificar_apostrofes(texto)
    texto = _expandir_contracciones(texto)
    texto = PATRON_NO_ASCII.sub(" ", texto)
    texto = PATRON_PUNTUACION.sub(" ", texto)
    return PATRON_ESPACIOS.sub(" ", texto).strip()


def normalizar_para_sentimiento(texto):
    """
    Version conservadora del texto: la que alimenta el analisis de sentimiento.

    Solo quita lo que no es lenguaje (URLs, handles, el simbolo #). Conserva a
    proposito la puntuacion, las mayusculas y las negaciones, ya que son
    justamente las senales que lee un analizador de sentimiento. Si se usara
    aca la version agresiva, un texto donde "not" ya fue eliminado como
    stopword se puntuaria con el sentido invertido.
    """
    if not isinstance(texto, str):
        return ""

    texto = PATRON_URL.sub(" ", texto)
    texto = PATRON_RETWEET.sub(" ", texto)
    texto = PATRON_MENCION.sub(" ", texto)
    texto = texto.replace("#", " ")
    texto = _unificar_apostrofes(texto)
    texto = PATRON_NO_ASCII.sub(" ", texto)
    return PATRON_ESPACIOS.sub(" ", texto).strip()


def tokenizar(texto_limpio, stopwords, raiz, minimo_caracteres=3):
    """
    Convierte el texto ya normalizado en la lista de tokens final.

    Quita los tokens que son solo numeros, las stopwords y los tokens muy
    cortos, y reduce cada palabra a su raiz. El parametro raiz es la funcion
    que hace esa reduccion, de tal forma que la etapa 06 le pasa el
    lematizador de WordNet y la 07 le pasa el stemmer de Snowball, y ambas
    comparten el resto del filtrado sin duplicarlo.

    El token de emergencia sobrevive porque no es un numero puro.
    """
    if not isinstance(texto_limpio, str) or not texto_limpio:
        return []

    tokens = []
    for token in texto_limpio.split():
        if PATRON_TOKEN_NUMERICO.match(token):
            continue
        if token in stopwords:
            continue
        base = raiz(token)
        # Se vuelve a comprobar despues porque WordNet trata ciertos tokens
        # como plurales y los deja numericos: 100s -> 100.
        if PATRON_TOKEN_NUMERICO.match(base):
            continue
        if len(base) < minimo_caracteres and base != TOKEN_EMERGENCIA:
            continue
        if base in stopwords:
            continue
        tokens.append(base)
    return tokens
