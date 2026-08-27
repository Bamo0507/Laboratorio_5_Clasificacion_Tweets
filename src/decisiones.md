# De dónde salen las decisiones de este pipeline

Este documento existe para dejar claro, desde el propio directorio del código, que
**ninguna de las transformaciones que hacen estas etapas se decidió por criterio propio
ni por costumbre**. Todas salen de haber medido primero el dataset, y esa medición está
en el notebook de análisis previo:

> `../notebooks/analisis_pre.ipynb`


---

## Por qué se hizo así

Considero que la tentación natural al limpiar texto es aplicar la receta de siempre, es
decir minúsculas, quitar URLs, quitar puntuación y quitar stopwords, sin preguntarse si
este dataset en particular la necesita toda. El problema es que esa receta se aplica a
ciegas y termina haciendo dos cosas malas a la vez: gasta esfuerzo en tareas que acá no
aplican, y adicional, destruye información que sí importaba.

Bajo esta idea se hizo primero el análisis exploratorio, midiendo qué tan sucio venía
realmente el texto y cuánto pesaba cada problema, y solo después se escribió el pipeline.
El orden no es cosmético, ya que tres de las decisiones que se tomaron **contradicen lo
que sugiere el enunciado del laboratorio**, y no habría forma de defenderlas sin el
número que las respalda.

---

## Las decisiones que salieron de medir, y no de suponer

### No se implementó la eliminación de emojis

El enunciado pide revisar si hay emoticones y quitarlos. Al medirlo resultó que **no hay
ni un solo emoji unicode en el dataset**, de tal forma que se habría escrito código para
un caso que nunca ocurre. Se dejó documentado que se verificó y que no había nada que
quitar, en lugar de agregar un paso decorativo al pipeline.

*Respaldo: sección 2.4 del notebook, tabla de patrones de ruido.*

### No se conservan los emoticones ASCII para el análisis de sentimiento

El enunciado pregunta, en su punto 8, si valdrá la pena dejar los emoticones para poder
analizarlos. La respuesta se midió: son **menos de 60 sobre 7,485 tweets**, o sea menos
del 1%, y adicional, una búsqueda ingenua los sobrecuenta porque el `://` de las URLs
coincide con el patrón. Con esa cantidad no pueden mover ninguna métrica, así que la
pregunta queda respondida a partir de los datos y no por opinión.

*Respaldo: sección 2.4 del notebook, celda de emoticones ASCII.*

### Se hace una excepción con el 911 y sus variantes

Este es el caso que mejor ilustra por qué convenía medir antes. El enunciado invita a
valorar si se quita o no el `911`, y al buscarlo resultó que aparece en apenas 4 tweets,
sin embargo al ampliar la búsqueda se encontró que el mismo evento se escribe también
como `9/11`, `9-11` y `WTC`, sumando **11 tweets, de los cuales 8 son de la clase 1**.

Ahora bien, lo importante no fue el conteo sino un detalle de orden de operaciones: la
secuencia habitual de limpieza **elimina el término en dos pasos sin que uno se dé
cuenta**, ya que quitar la puntuación parte `9/11` en `9` y `11`, y el paso siguiente los
borra por ser números. Es decir que uno podría creer que decidió conservarlo y aun así
perderlo. Es por esto que `texto.py` normaliza todas las variantes a un token único e
irrompible **antes** de tocar la puntuación.

Cabe mencionar que hay que ser honestos con el alcance, pues 11 tweets no van a mover
ninguna métrica. La excepción no se implementó esperando ganar accuracy, sino porque el
enunciado pide valorar el caso y porque el episodio dejó ver un riesgo general del
pipeline, y es que el orden de los pasos destruye información en silencio.

*Respaldo: sección 2.4 del notebook, celdas de números y de la secuencia de limpieza.*

### Se corrige el mojibake, que el enunciado ni siquiera menciona

Al inspeccionar los tweets crudos aparecieron secuencias como `\x89Ûª` y `\x89ÛÏ` en el
**8.07% de los casos**. No son texto, sino comillas y guiones que quedaron mal
codificados al armar el dataset original. Ninguna de las tareas de limpieza que sugiere
el enunciado las resuelve, y si no se tratan el tokenizador las convierte en basura que
contamina el vocabulario, o peor, parte una palabra en dos, ya que `don\x89Ûªt` deja de
reconocerse como `dont`.

Adicional, se probó `ftfy`, que es el módulo estándar para este tipo de problema, y no lo
resolvió, pues convierte `\x89` en `‰` pero deja el resto de la secuencia intacta. Por eso
la tabla de reemplazos de `02_codificacion.py` se dedujo a mano leyendo cada secuencia en
su contexto real, por ejemplo `Can\x89Ûªt` que corresponde a `Can't`.

*Respaldo: sección 2.4 del notebook, celda de mojibake.*

### Se extrae la señal del texto antes de limpiarlo

El enunciado manda quitar URLs y menciones, y efectivamente hay que hacerlo porque una
URL de `t.co` es una cadena aleatoria que como token sería única e inútil. Sin embargo,
al medirlo se encontró que **entre los tweets sin URL solo el 30% son desastre real,
contra un 55% entre los que sí la traen**, o sea que el hecho de que existiera una URL sí
es informativo aunque la cadena no lo sea.

Dado el caso, la etapa `04_features_crudas.py` corre **antes** de la limpieza y registra
esa presencia en variables de conteo, de tal forma que se elimina la cadena pero se
conserva la señal. Lo mismo aplica a las mayúsculas, que el paso a minúsculas borra sin
dejar rastro.

*Respaldo: sección 2.6 del notebook, comparación de medias por clase.*

### Se producen dos versiones del texto y no una

Esta es la consecuencia de todo lo anterior. El preprocesamiento agresivo que necesita el
clasificador destruye justamente lo que el análisis de sentimiento necesita leer, que son
las negaciones, la intensidad y los signos. Sin esta separación, el ejercicio 8 puntuaría
un texto donde `not` ya fue eliminado como stopword, invirtiendo el sentido de cada frase
negada.

Es por esto que `05_limpieza_texto.py` genera `texto_limpio` y `texto_sentimiento`, cada
una con su propio nivel de agresividad.

### Se descarta `location` como predictora, pero no se borra la columna

Se midió que tiene un 33% de faltantes y 3,341 valores únicos sobre 5,080 presentes, casi
todos irrepetibles, y que es campo libre sin validar donde conviven `USA`, `US` y
`United States` junto con bromas y basura. Normalizarla exigiría geocodificación externa,
y aun así la ubicación del emisor no determina si el tweet habla de un desastre.

No obstante, la columna se conserva en el dataset final, ya que descartarla dentro de la
limpieza impondría una decisión de modelado sobre cualquier análisis posterior. Que no se
use es una decisión que se toma al modelar, no al limpiar.

*Respaldo: sección 2.3 del notebook.*

---

## Lo que las validaciones atraparon

Las llamadas a `afirmar` que hay en cada etapa no son decorativas, y durante el
desarrollo detuvieron el pipeline dos veces por errores que en un script monolítico
habrían pasado desapercibidos:

1. La etapa 05 se detuvo porque quedaban **guiones bajos** en `texto_limpio`. La causa era
   que `\w` considera el guion bajo un carácter de palabra, de tal forma que la expresión
   de puntuación no lo tocaba, y en los handles termina uniendo palabras reales como
   `our_mother_mary`.
2. La etapa 06 se detuvo porque quedaban **tokens puramente numéricos** que se suponían
   eliminados. La causa era que el lematizador de WordNet trata `100s` como plural y lo
   convierte en `100`, o sea que el token numérico nacía *después* del filtro que debía
   quitarlo. Es por esto que ahora la comprobación se hace dos veces, antes y después de
   lematizar.

Ambos casos refuerzan la idea de fondo de este documento: las decisiones se sostienen
porque se midieron y porque el pipeline verifica que efectivamente se cumplieron.

---

## Cómo mantener esto al día

Si se agrega o se cambia una transformación, la referencia al notebook deja de ser válida
y hay que actualizarla. Bajo este escenario conviene seguir el mismo orden que se usó
acá: primero se mide en el notebook de análisis previo, luego se escribe la etapa, y
después se cita la sección en el docstring de la etapa y en este documento.

El detalle de cada regla aplicada, con sus conteos exactos, está en
[`../codebook.md`](../codebook.md), y la descripción del pipeline como tal está en
[`../README.md`](../README.md).
