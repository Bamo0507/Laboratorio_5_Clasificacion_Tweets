"""
Configuracion del entregable: rutas y contratos de columnas.
------------------------------------------------------------
Unica fuente de verdad. Ningun script inventa sus propias rutas ni
redefine que columnas debe tener el dataset en cada punto del pipeline.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"

# ---------------------------------------------------------------- rutas
RUTA_CRUDA        = DIR_RAW / "train.csv"                     # entrada, nunca se modifica
RUTA_INGESTA      = DIR_PROCESSED / "01_ingesta.csv"          # <- 01_ingesta.py
RUTA_CODIFICACION = DIR_PROCESSED / "02_codificacion.csv"     # <- 02_codificacion.py
RUTA_INTEGRIDAD   = DIR_PROCESSED / "03_integridad.csv"       # <- 03_integridad.py
RUTA_FEATURES     = DIR_PROCESSED / "04_features_crudas.csv"  # <- 04_features_crudas.py
RUTA_TEXTO        = DIR_PROCESSED / "05_texto_limpio.csv"     # <- 05_limpieza_texto.py
RUTA_FINAL        = DIR_PROCESSED / "tweets_procesado.csv"    # <- 06_tokenizacion.py
RUTA_STEMMING     = DIR_PROCESSED / "07_stemming.csv"         # <- 07_stemming.py
RUTA_TRAIN        = DIR_PROCESSED / "train_modelado.csv"      # <- 08_particion.py
RUTA_TEST         = DIR_PROCESSED / "test_modelado.csv"       # <- 08_particion.py

# ---------------------------------------------------------------- contratos de columnas
# Lo que DEBE traer el archivo crudo de Kaggle.
COLUMNAS_CRUDAS = ["id", "keyword", "location", "text", "target"]

# Variables derivadas que extrae la etapa 04 sobre el texto todavia sin limpiar.
COLUMNAS_FEATURES = [
    "tiene_url",
    "n_hashtags",
    "n_menciones",
    "n_caracteres",
    "n_palabras",
    "n_mayusculas",
]

# Las dos versiones del texto que produce la etapa 05.
COLUMNAS_TEXTO = ["texto_limpio", "texto_sentimiento"]

# Columna final de la etapa 06 (lematizacion) y su equivalente con stemming (etapa 07).
COLUMNA_TOKENS = "tokens"
COLUMNA_TOKENS_STEM = "tokens_stem"

# Particion de la etapa 08.
PROPORCION_PRUEBA = 0.30
SEMILLA = 123

# ---------------------------------------------------------------- parametros del dominio
# Etiquetas validas de la variable objetivo.
TARGET_VALIDOS = {0, 1}

# Cantidad de filas del crudo de Kaggle. Sirve de chequeo en la ingesta.
FILAS_CRUDAS_ESPERADAS = 7613
