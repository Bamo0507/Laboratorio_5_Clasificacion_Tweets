"""
Etapa 9 del pipeline: ANALISIS DE SENTIMIENTO
------------------------------------------------------------
Una sola responsabilidad: puntuar el sentimiento de cada tweet y dejar la
variable de negatividad lista para el ejercicio 10.

  Lee : data/processed/train_modelado.csv
        data/processed/test_modelado.csv
  Hace: - cuenta palabras positivas y negativas segun el lexico de VADER
        - calcula el puntaje compuesto y clasifica en positivo/negativo/neutro
        - deriva negatividad, que es el componente "neg" de VADER en [0, 1]
  Escribe: data/processed/09_sentimiento_train.csv
           data/processed/09_sentimiento_test.csv

Escribe archivos propios y NO sobre sus entradas. Antes esta etapa sobrescribia
train_modelado.csv y test_modelado.csv, de tal forma que volver a correr solo
la etapa 08 borraba en silencio las columnas de sentimiento y el notebook de
los ejercicios 8, 9 y 10 dejaba de funcionar.

La logica vive en sentimiento.py para que el notebook use exactamente la misma,
ya que estaba duplicada y las dos copias habian divergido.

Se descarto conservar los emoticones ASCII: decisiones.md ya midio que aparecen
en menos del 1% de los tweets, asi que no habria como moverle el resultado.

Ejecutar:  python src/09_sentimiento.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
import sentimiento as snt
from utils import afirmar, afirmar_columnas, banner, cargar, guardar

banner("Etapa 9: analisis de sentimiento")

train = cargar(config.RUTA_TRAIN)
test = cargar(config.RUTA_TEST)
for conjunto, nombre in ((train, "train"), (test, "test")):
    afirmar_columnas(conjunto, ["texto_sentimiento", "target"],
                     f"contrato de la etapa 08 ({nombre})")

train = snt.puntuar_dataframe(train)
test = snt.puntuar_dataframe(test)

afirmar_columnas(train, snt.COLUMNAS, "salida de la etapa 09")
afirmar(train["negatividad"].between(0, 1).all() and test["negatividad"].between(0, 1).all(),
        "negatividad queda en el rango [0, 1]")
afirmar(set(train["sentimiento_clase"]) <= {"positivo", "negativo", "neutro"},
        "la clasificacion de sentimiento solo usa las tres etiquetas esperadas")
afirmar((train[["n_palabras_positivas", "n_palabras_negativas"]] >= 0).all().all(),
        "los conteos de palabras son no negativos")

distribucion = train["sentimiento_clase"].value_counts()
print(f"[ok]       distribucion de sentimiento (train): {distribucion.to_dict()}")
print(f"[ok]       compound medio por clase (train): "
      f"{train.groupby('target')['sentimiento_compound'].mean().round(4).to_dict()}")

guardar(train, config.RUTA_SENTIMIENTO_TRAIN)
guardar(test, config.RUTA_SENTIMIENTO_TEST)
