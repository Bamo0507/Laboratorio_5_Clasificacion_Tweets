# Laboratorio 5 — Clasificación de tweets usando minería de texto

## Dónde está resuelto cada ejercicio

| # | Ejercicio | Dónde está |
|---|---|---|
| 1 | Descargar `train.csv` | `data/raw/train.csv` |
| 2 | Cargar los datos | `src/01_ingesta.py` · descripción de las 5 variables en `notebooks/analisis_pre.ipynb` (§1) |
| 3 | Limpieza y preprocesamiento | `src/01_` a `src/06_` · el porqué de cada decisión en [`src/decisiones.md`](src/decisiones.md) · medición previa en `notebooks/analisis_pre.ipynb` |
| 4 | Frecuencias de n-gramas | `notebooks/4_frecuencias_tweets.ipynb` |
| 5 | Análisis exploratorio | `notebooks/5_analisis_exploratorio.ipynb` |
| 6 | Modelos de clasificación | `notebooks/6_modelos_clasificacion.ipynb` · partición en `src/08_particion.py` |
| 7 | Función de clasificación | `notebooks/7_funcion_clasificacion.ipynb` (`clasificar_tweet`) |
| 8 | Sentimiento positivo/negativo/neutro | `notebooks/8_9_10_sentimiento.ipynb` · lógica en `src/sentimiento.py` · etapa `src/09_sentimiento.py` |
| 9 | Tweets más negativos y más positivos | `notebooks/8_9_10_sentimiento.ipynb` (§9.1, §9.2, §9.3) |
| 10 | Variable de negatividad y reentrenamiento | `notebooks/8_9_10_sentimiento.ipynb` (§10) |
| 11 | Informe | `Informe.pdf` |

Los notebooks se leen en orden numérico. `analisis_pre.ipynb` va antes que todos: es el análisis
que se hizo **antes** de escribir el pipeline, y es el que justifica las decisiones de limpieza.

---

## Estructura del repositorio

```
├── data/
│   ├── raw/                  train.csv de Kaggle, intacto, se versiona
│   └── processed/            generado por el pipeline, NO se versiona
├── notebooks/                análisis y modelado (ejercicios 4 a 10)
├── src/                      pipeline de datos por etapas
├── codebook.md               diccionario del dataset final
└── requirements.txt
```

### El pipeline

```
data/raw/train.csv                                    7,613 filas, 5 columnas
   |
   v  01_ingesta.py            carga con dtype=str y valida el contrato del crudo
   v  02_codificacion.py       revierte mojibake, entidades HTML y el %20 de keyword
   v  03_integridad.py         descarta contradictorios y duplicados      7,485 filas
   v  04_features_crudas.py    extrae la señal ANTES de que la limpieza la destruya
   v  05_limpieza_texto.py     produce texto_limpio y texto_sentimiento
   v  06_tokenizacion.py       stopwords, números y lematización
   v  07_stemming.py           variante con stemming, para comparar en el ejercicio 6
   v  08_particion.py          70/30 estratificada, semilla fija
   v  09_sentimiento.py        VADER: sentimiento y variable de negatividad
                               09_sentimiento_train.csv  ·  09_sentimiento_test.csv
```

| Etapa | Archivo | Responsabilidad |
|---|---|---|
| 1 | `01_ingesta.py` | Cargar el crudo intacto y validar su contrato |
| 2 | `02_codificacion.py` | Reparar la codificación corrompida |
| 3 | `03_integridad.py` | Una fila por tweet con etiqueta confiable |
| 4 | `04_features_crudas.py` | Medir la señal del texto sin limpiar |
| 5 | `05_limpieza_texto.py` | Normalizar el texto en dos versiones |
| 6 | `06_tokenizacion.py` | Tokens finales con lematización |
| 7 | `07_stemming.py` | La misma tokenización pero con stemming |
| 8 | `08_particion.py` | Partición 70/30 estratificada |
| 9 | `09_sentimiento.py` | Puntaje de sentimiento y negatividad |
