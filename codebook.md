# Codebook — dataset de modelado

Diccionario de datos del dataset final del pipeline, que cubre los **ejercicios 3, 8 y 10**
(limpieza, preprocesamiento, sentimiento y variable de negatividad).

**Archivos documentados:**

| Archivo | Filas | Columnas | Para qué |
|---|---|---|---|
| `data/processed/09_sentimiento_train.csv` | 5,239 | 21 | Entrenamiento (70%) |
| `data/processed/09_sentimiento_test.csv` | 2,246 | 21 | Prueba (30%) |

Ambos comparten el mismo esquema y solo se diferencian en qué filas les tocaron. La partición es
estratificada por `target`, de tal forma que la tasa de desastre queda en 0.4258 en entrenamiento y
0.4261 en prueba. Antes de partirse, el dataset completo son 7,485 filas.

También quedan en disco los archivos intermedios `tweets_procesado.csv` (salida de la etapa 06) y
`07_stemming.csv`, que son el mismo dataset sin partir y sin las columnas de sentimiento.

**Cómo se genera:** corriendo `python src/run_pipeline.py`, que encadena

```
data/raw/train.csv
  -> 01_ingesta.py -> 02_codificacion.py -> 03_integridad.py -> 04_features_crudas.py
  -> 05_limpieza_texto.py -> 06_tokenizacion.py -> 07_stemming.py -> 08_particion.py
  -> 09_sentimiento.py
  -> data/processed/09_sentimiento_train.csv
     data/processed/09_sentimiento_test.csv
```

**Fuente del crudo:** competencia [*Natural Language Processing with Disaster Tweets*](https://www.kaggle.com/competitions/nlp-getting-started/data)
de Kaggle, archivo `train.csv` (7,613 filas). El `test.csv` de la competencia no se usa porque no
trae la variable objetivo, de tal forma que el conjunto de prueba sale de particionar el train.

---

## Tabla de variables

| Variable | Tipo | Descripción | Valores válidos / notas |
|---|---|---|---|
| `id` | `int64` | Identificador único del tweet, heredado de Kaggle. | Entero positivo, único. No es correlativo, ya que Kaggle repartió los ids entre train y test. Sin valor predictivo. |
| `keyword` | `str` | Palabra clave asociada al tweet. | 221 categorías. **Derivada parcialmente:** en el crudo venía codificada como URL y la etapa 02 le decodificó el `%20`. 56 faltantes. |
| `location` | `str` | Ubicación declarada por el usuario. | Campo libre sin validar. 2,472 faltantes. **No se usa como predictora**, ver la justificación abajo. |
| `text` | `str` | Texto del tweet. | **Reparado en la etapa 02**: ya no tiene mojibake ni entidades HTML. Fuera de eso conserva la forma original. Sin faltantes. |
| `target` | `int64` | **Variable objetivo.** Indica si el tweet habla de un desastre real. | `1` = desastre real (42.59%), `0` = no (57.41%). Sin faltantes. |
| `tiene_url` | `int64` | Si el tweet original traía al menos una URL. | **Derivada** en la etapa 04. Binaria: `0` o `1`. Media 0.53. |
| `n_hashtags` | `int64` | Cantidad de hashtags del tweet original. | **Derivada.** Rango 0 a 13, media 0.43. |
| `n_menciones` | `int64` | Cantidad de menciones `@usuario`. | **Derivada.** Rango 0 a 8, media 0.36. |
| `n_caracteres` | `int64` | Largo del tweet original en caracteres. | **Derivada.** Rango 7 a 157, media 100.53. |
| `n_palabras` | `int64` | Cantidad de palabras del tweet original. | **Derivada.** Rango 1 a 31, media 14.88. |
| `n_mayusculas` | `int64` | Palabras de 3 o más letras escritas todas en mayúscula. | **Derivada.** Rango 0 a 20, media 0.50. |
| `texto_limpio` | `str` | Versión agresiva del texto. | **Derivada** en la etapa 05. Solo minúsculas, dígitos y espacios. Alimenta n-gramas y modelos. |
| `texto_sentimiento` | `str` | Versión conservadora del texto. | **Derivada** en la etapa 05. Conserva puntuación, mayúsculas y negaciones. Alimenta el análisis de sentimiento del ejercicio 8. |
| `tokens` | `str` | Tokens finales separados por espacio. | **Derivada** en la etapa 06. Sin stopwords, sin números y lematizados. 3 faltantes, que son tweets que quedaron sin ningún token. |
| `n_tokens` | `int64` | Cantidad de tokens de la columna anterior. | **Derivada.** Rango 0 a 21, media 8.37. Vale `0` en los 3 tweets sin tokens. |
| `tokens_stem` | `str` | Los mismos tokens pero reducidos con stemming en lugar de lematización. | **Derivada** en la etapa 07. Existe para poder comparar ambos enfoques en el ejercicio 6. 3 faltantes, los mismos tweets que quedaron sin tokens. |
| `n_palabras_positivas` | `int64` | Palabras del tweet que están en el léxico de VADER con signo positivo. | **Derivada** en la etapa 09. Rango 0 a 7, media 0.56. |
| `n_palabras_negativas` | `int64` | Palabras del tweet que están en el léxico de VADER con signo negativo. | **Derivada** en la etapa 09. Rango 0 a 13, media 0.93. |
| `sentimiento_compound` | `float64` | Puntaje compuesto de VADER, que resume la polaridad del tweet. | **Derivada** en la etapa 09. Rango observado -0.9883 a 0.9730, media -0.1444. Escala teórica [-1, 1]. |
| `negatividad` | `float64` | Proporción del tweet que VADER considera negativa. Es la variable del ejercicio 10. | **Derivada** en la etapa 09, componente `neg` de VADER. Rango 0 a 1, media 0.1591. |
| `sentimiento_clase` | `str` | Clasificación del tweet en positivo, negativo o neutro. | **Derivada** en la etapa 09 a partir de `sentimiento_compound`. Valores: `negativo` (3,697), `positivo` (1,937), `neutro` (1,851). |

Vocabulario con lematización: **12,735 términos distintos**. Con stemming: **10,958**, es decir un
14% más compacto.

---

## Reglas de limpieza aplicadas

### Etapa 02 — corrección de codificación

- **Mojibake revertido en 614 tweets (8.07%).** Las secuencias `\x89Û_`, `\x89Ûª`,
  `\x89ÛÏ`, `\x89Û\x9d`, `\x89Û÷`, `\x89ÛÒ`, `\x89ÛÓ` y `\x89Û¢` no son texto, sino
  comillas tipográficas, guiones, puntos suspensivos y viñetas que quedaron mal
  codificados al armar el dataset original. Se mapearon leyendo cada secuencia en su
  contexto real, por ejemplo `Can\x89Ûªt` que corresponde a `Can't` y
  `\x89ÛÏAirplane\x89Û\x9d` que corresponde a `"Airplane"`. La tabla completa está en
  `src/02_codificacion.py`. Se corrigió antes que todo lo demás porque el mojibake
  parte palabras en dos y contaminaría el vocabulario.
- **Entidades HTML decodificadas en 359 tweets (4.72%)** con `html.unescape`.
- **`%20` decodificado en 1,165 keywords** con `urllib.parse.unquote`.

### Etapa 03 — integridad

- **Descartados 18 textos con etiquetas contradictorias (55 filas).** El mismo tweet
  aparecía marcado como desastre y como no desastre, y dado que no hay forma de saber
  cuál etiqueta es la correcta se descartaron todas sus apariciones en lugar de elegir
  una al azar.
- **Eliminados 73 duplicados de `text`**, conservando la primera aparición.
- **Tipado:** `id` y `target` pasaron de texto a entero.

El total descartado fue de **128 filas: 7,613 a 7,485**. La tasa de desastre pasó de
0.4297 a 0.4259, o sea que el balance de clases prácticamente no se movió.

### Etapa 05 — normalización del texto

El orden de los pasos no es intercambiable, y esto es lo más delicado de la limpieza.

1. **Normalización de las variantes de emergencia.** `911`, `9/11`, `9-11` y `WTC` se
   reemplazan por el token único `emergencia911`. Va primero porque los pasos siguientes
   lo destruirían: quitar la puntuación parte `9/11` en `9` y `11`, y quitar números
   borra los dos. Sobrevivió en 11 tweets.
2. **URLs eliminadas** (52.16% de los tweets). La cadena de `t.co` es aleatoria y como
   token sería única e inútil, no obstante su presencia ya quedó guardada en `tiene_url`.
3. **Prefijo `RT` y menciones `@usuario` eliminados.** Los handles son identificadores,
   no vocabulario.
4. **Símbolo `#` eliminado pero la palabra conservada**, de tal forma que `#earthquake`
   queda como `earthquake`. Es el único símbolo que no se borra junto con su contenido,
   ya que el hashtag suele ser el término más informativo del tweet.
5. **Paso a minúsculas**, después de que la etapa 04 contara las mayúsculas.
6. **Apóstrofes tratados antes de quitar puntuación.** Se unifican los curvos con el
   recto, se expanden las contracciones frecuentes (`don't` a `do not`) y el resto pierde
   el apóstrofe uniéndose. Sin esto aparece el token basura `s`.
7. **Caracteres no ASCII y puntuación eliminados.** El guion bajo se trata como
   puntuación aunque `\w` lo considere carácter de palabra, porque en los handles une
   palabras reales (`our_mother_mary`).
8. **Espacios múltiples colapsados.**

`texto_sentimiento` aplica solo los pasos 2, 3 y 4 más el colapso de espacios, y conserva
a propósito puntuación, mayúsculas y negaciones.

### Etapa 06 — tokenización

- **Tokens puramente numéricos eliminados.** Se comprueba dos veces, antes y después de
  lematizar, ya que WordNet trata ciertos tokens como plurales y los deja numéricos, por
  ejemplo `100s` que se convierte en `100`.
- **Stopwords en inglés eliminadas** con el corpus de NLTK (198 palabras).
- **Tokens de menos de 3 caracteres eliminados**, con excepción de `emergencia911`.
- **Lematización con WordNet** para poder unificar `fires` y `fire` en un mismo término.

### Etapa 07 — variante con stemming

- **Se aplica el `SnowballStemmer` de NLTK** sobre `texto_limpio`, con exactamente el mismo filtrado
  que usó la lematización, ya que la función `tokenizar` de `src/texto.py` recibe la reducción como
  parámetro y por eso ambas variantes comparten el resto del proceso.
- La lematización devuelve una palabra real, es decir `fires` queda como `fire`, mientras que el
  stemming corta a la raíz aunque no exista, de tal forma que `disaster` queda como `disast`. Cuál
  funciona mejor depende del corpus, y por eso no se elige de antemano sino que se comparan las dos
  en el ejercicio 6.

### Etapa 08 — partición entrenamiento / prueba

- **Partición estratificada 70/30 por `target`**, con semilla fija en `config.SEMILLA`.
- Se hace en el pipeline y no dentro de los notebooks para poder garantizar que todos los modelos
  del ejercicio 6 se evalúan sobre exactamente las mismas filas, ya que si cada quien partiera por
  su cuenta las métricas no serían comparables entre sí.

### Etapa 09 — análisis de sentimiento

- **Se puntúa con VADER** (`vaderSentiment`) y no con TextBlob, porque su léxico y sus reglas están
  hechos para texto de redes sociales: ponderan mayúsculas, puntuación repetida, negaciones e
  intensificadores.
- **Se corre sobre `texto_sentimiento` y no sobre `tokens`**, ya que VADER necesita mayúsculas,
  puntuación y negaciones intactas. Usar la versión agresiva invertiría el sentido de cada frase
  negada, dado que `not` se elimina como stopword.
- **Al contar palabras del léxico se busca el token completo antes de recortarle la puntuación**,
  porque los emoticones están en el léxico con sus signos incluidos y recortarlos los destruiría, de
  tal forma que `:)` se volvería `:`.
- La clasificación en positivo, negativo o neutro sale del puntaje compuesto y no del conteo crudo
  de palabras, ya que el compuesto aplica las reglas de negación e intensidad que el conteo ignora.
  Por ejemplo, `not good` suma una palabra positiva en el conteo y sin embargo el compuesto lo
  puntúa como negativo.
- La lógica vive en `src/sentimiento.py` para que la etapa y el notebook usen la misma, pues estuvo
  duplicada y las dos copias divergieron.

---

## Política de valores faltantes

Siguiendo el estándar del curso, en la limpieza **no se imputó ningún valor** y **no se
eliminó ninguna fila por tener faltantes**, pues rellenar es una decisión de análisis que
corresponde tomar y justificar en el EDA, no antes de haber visto los datos.

Los faltantes del dataset final se clasifican así:

| Variable | Faltantes | Clasificación |
|---|---|---|
| `keyword` | 56 | **Ausente en el origen.** Kaggle no asignó palabra clave a esos tweets, de tal forma que `NaN` es la representación honesta. |
| `location` | 2,472 | **Ausente en el origen.** El usuario no declaró ubicación en su perfil. |
| `tokens_stem` | 3 | **Propagación correcta.** Los mismos tweets que quedaron sin `tokens`. |
| `tokens` | 3 | **Propagación correcta.** Son tweets cuyo contenido era enteramente URLs, menciones o stopwords, así que al limpiarlos no quedó ningún token. No es un faltante nuevo sino la consecuencia esperada de la limpieza. Su `n_tokens` vale `0`. |

Las 128 filas descartadas en la etapa 03 no se fueron por faltantes sino por violar una
regla dura, y quedan documentadas arriba.

---

## Nota sobre `location`

`location` se conserva en el dataset final aunque **no se usará como predictora**, y la
distinción importa: descartar una columna en la limpieza impondría una decisión de
modelado sobre cualquier análisis posterior, mientras que dejarla permite que quien
quiera usarla la tenga disponible.

La razón para no usarla, medida en `notebooks/analisis_pre.ipynb` sección 2.3, es que tiene un 33%
de faltantes y 3,341 valores únicos sobre 5,080 presentes, la mayoría irrepetibles. Es
campo libre sin validar, de tal forma que conviven `USA`, `US` y `United States` como
entradas distintas junto con bromas y basura. Normalizarla exigiría geocodificación
externa, y aun así considero que la ubicación del emisor no determina si el tweet habla
de un desastre, ya que se puede tuitear sobre un huracán desde cualquier lugar.

---

## Fuente de los datos

Kaggle, competencia *Natural Language Processing with Disaster Tweets*:
<https://www.kaggle.com/competitions/nlp-getting-started/data>
