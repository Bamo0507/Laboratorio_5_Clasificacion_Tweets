"""
Etapa 2 del pipeline: CORRECCION DE CODIFICACION
------------------------------------------------------------
Una sola responsabilidad: reparar el texto que llego con la codificacion
corrompida, sin alterar todavia su contenido ni su forma.

  Lee : data/processed/01_ingesta.csv
  Hace: - revierte el mojibake de text (secuencias \\x89U... que en realidad
          son comillas tipograficas, guiones y puntos suspensivos)
        - decodifica las entidades HTML (&amp; -> &)
        - decodifica el %20 de keyword (airplane%20accident -> airplane accident)
  Escribe: data/processed/02_codificacion.csv

El EDA (notebooks/analisis_pre.ipynb, seccion 2.4) midio que el mojibake afecta al
8.07% de los tweets y las entidades HTML al 4.72%. Va antes que todo lo demas
porque el mojibake parte palabras en dos: don\\x89Uat no se reconoce como dont.

Ejecutar:  python src/02_codificacion.py
"""

import html
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from utils import afirmar, afirmar_columnas, banner, cargar, guardar

# Tabla de mojibake. Se dedujo leyendo cada secuencia en su contexto real
# (ver notebooks/analisis_pre.ipynb, seccion 2.4): Can\x89Uat -> Can't,
# \x89UOAirplane\x89U\x9d -> "Airplane", JAMAICA \x89UO -> JAMAICA -.
# El orden importa: las secuencias largas se reemplazan antes que el
# residuo generico "\x89\xdb", que va de ultimo como red de seguridad.
MOJIBAKE = [
    ("\x89\xdb\x9d", '"'),   # comilla doble de cierre
    ("\x89\xdb\xcf", '"'),   # comilla doble de apertura
    ("\x89\xdb\xaa", "'"),   # apostrofe / comilla simple de cierre
    ("\x89\xdb\xf7", "'"),   # comilla simple de apertura
    ("\x89\xdb\xd2", "-"),   # guion corto
    ("\x89\xdb\xd3", "-"),   # guion largo
    ("\x89\xdb_",    "..."), # puntos suspensivos (marca de truncado del tweet)
    ("\x89\xdb\xa2", "*"),   # vineta
    ("\x89\xe3\xa2", ""),    # residuo poco frecuente
    ("\x89\xe2\xc2", "..."), # residuo poco frecuente
    ("\xe5\xca",     " "),   # espacio duro mal codificado
    ("\x89\xdb",     ""),    # residuo generico, siempre de ultimo
]


def corregir_mojibake(texto):
    """Revierte las secuencias corrompidas a su caracter original."""
    for corrupto, correcto in MOJIBAKE:
        texto = texto.replace(corrupto, correcto)
    return texto


def decodificar_url(valor):
    """airplane%20accident -> airplane accident. Respeta los NaN."""
    if not isinstance(valor, str):
        return valor
    return urllib.parse.unquote(valor)


def main():
    banner("Etapa 2: correccion de codificacion")

    df = cargar(config.RUTA_INGESTA, dtype=str)
    afirmar_columnas(df, config.COLUMNAS_CRUDAS, "contrato de la etapa 01")

    antes_mojibake = df["text"].str.contains("\x89", na=False).sum()
    antes_html = df["text"].str.contains(r"&(?:amp|lt|gt|quot|#\d+);", regex=True, na=False).sum()
    antes_pct20 = df["keyword"].str.contains("%20", na=False).sum()

    df["text"] = df["text"].map(corregir_mojibake)
    df["text"] = df["text"].map(html.unescape)
    df["keyword"] = df["keyword"].map(decodificar_url)

    print(f"[ok]       mojibake corregido en {antes_mojibake:,} tweets")
    print(f"[ok]       entidades HTML decodificadas en {antes_html:,} tweets")
    print(f"[ok]       %20 decodificado en {antes_pct20:,} keywords")

    afirmar(not df["text"].str.contains("\x89", na=False).any(),
            "no queda ninguna secuencia de mojibake en text")
    afirmar(not df["keyword"].str.contains("%20", na=False).any(),
            "no queda ningun %20 en keyword")
    afirmar(df["text"].notna().all() and len(df) == config.FILAS_CRUDAS_ESPERADAS,
            "no se perdio ninguna fila ni quedo text vacio")

    guardar(df, config.RUTA_CODIFICACION)


main()
