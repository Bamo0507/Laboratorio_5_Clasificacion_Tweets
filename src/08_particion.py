"""
Etapa 8 del pipeline: PARTICION ENTRENAMIENTO / PRUEBA
------------------------------------------------------------
Una sola responsabilidad: partir el dataset en 70% de entrenamiento y 30% de
prueba, dejando los dos archivos fijos en disco.

  Lee : data/processed/07_stemming.csv
  Hace: - particion estratificada por target, con semilla fija
  Escribe: data/processed/train_modelado.csv
           data/processed/test_modelado.csv

La particion se hace aca y no dentro del notebook por dos razones. Primero,
para que todos los modelos del ejercicio 6 se evaluen sobre exactamente el
mismo conjunto de prueba, ya que si cada quien partiera por su cuenta las
metricas no serian comparables entre si. Segundo, porque el test.csv de la
competencia no trae la variable objetivo, de tal forma que el unico conjunto
de prueba posible sale de particionar el train.

Se estratifica por target para poder conservar la proporcion de clases en
ambos lados, dado que el dataset esta levemente desbalanceado (42.6% / 57.4%).

Modulo externo usado: scikit-learn (train_test_split).

Ejecutar:  python src/08_particion.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sklearn.model_selection import train_test_split

import config
from utils import afirmar, afirmar_columnas, banner, cargar, guardar

banner("Etapa 8: particion entrenamiento / prueba")

df = cargar(config.RUTA_STEMMING)
afirmar_columnas(df, [config.COLUMNA_TOKENS, config.COLUMNA_TOKENS_STEM, "target"],
                 "contrato de la etapa 07")

train, test = train_test_split(
    df,
    test_size=config.PROPORCION_PRUEBA,
    stratify=df["target"],
    random_state=config.SEMILLA,
)

afirmar(len(train) + len(test) == len(df), "la particion no perdio ni duplico filas")
afirmar(not set(train["id"]) & set(test["id"]), "no hay ids compartidos entre train y test")
afirmar(abs(train["target"].mean() - test["target"].mean()) < 0.01,
        "la estratificacion mantuvo la tasa de desastre en ambos conjuntos")

print(f"[ok]       entrenamiento: {len(train):,} filas ({len(train)/len(df)*100:.1f}%) | "
      f"tasa de desastre {train['target'].mean():.4f}")
print(f"[ok]       prueba       : {len(test):,} filas ({len(test)/len(df)*100:.1f}%) | "
      f"tasa de desastre {test['target'].mean():.4f}")
print(f"[ok]       semilla fija : {config.SEMILLA}")

guardar(train, config.RUTA_TRAIN)
guardar(test, config.RUTA_TEST)
