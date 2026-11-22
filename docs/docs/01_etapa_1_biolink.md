# BioLink — Etapa 1. Definición de la aplicación e investigación del dominio

**Proyecto integrador:** Diseño, desarrollo e integración de tres modelos de bases de datos  
**Etapa:** 1 de 10 — Definición de la aplicación  
**Versión del documento:** 1.0  
**Fecha de cierre documental:** 20 de noviembre de 2026  
**Estado:** Etapa 1 completada

---

## 1. Resumen ejecutivo

**BioLink** será una plataforma académica para consultar y explorar interacciones ecológicas documentadas entre especies, con énfasis inicial en la frugivoría y la evidencia de consumo o remoción de frutos por murciélagos y mamíferos terrestres en la zona sur de la Reserva de la Biosfera Montes Azules, Chiapas. El Ejido Playón de la Gloria se conservará como localidad externa de comparación cuando la fuente la identifique expresamente; sus registros nunca se presentarán como si ocurrieran dentro del área natural protegida.

El problema que atiende BioLink es la fragmentación de la información ecológica. Los datos de presencia de especies, las descripciones taxonómicas y las relaciones ecológicas suelen encontrarse en fuentes diferentes, con métodos, periodos, niveles de precisión geográfica y criterios de identificación distintos. Reunirlos sin conservar su procedencia puede producir relaciones incorrectas o dar una impresión de certeza mayor que la que ofrece la evidencia.

BioLink reunirá esos datos en una interfaz única, permitiendo:

- consultar fichas de taxones y sus fuentes;
- explorar relaciones ecológicas con filtros por localidad, periodo, método y tipo de evidencia;
- visualizar redes de interacción;
- comparar, cuando sea válido, el área de estudio dentro de Montes Azules con Playón de la Gloria;
- abrir la evidencia bibliográfica que respalda cada relación.

La propuesta justifica los tres modelos de bases de datos desde necesidades diferentes: el **relacional** para la administración íntegra de usuarios, fuentes, conjuntos de datos y procesos de revisión; el **documental** para conservar fichas y registros de origen con estructuras heterogéneas; y el **modelo de grafo** para recorrer y analizar las relaciones entre taxones, localidades y estudios.

> **Principio rector:** BioLink no afirmará que dos especies interactúan únicamente porque ambas estén registradas en la misma región. Cada relación positiva deberá estar respaldada por una fuente y un tipo de evidencia identificables.

## 2. Ficha de definición de la aplicación

| Elemento | Definición |
|---|---|
| Nombre | **BioLink** |
| Nombre descriptivo | Explorador de biodiversidad e interacciones ecológicas |
| Tipo de aplicación | Plataforma académica de consulta y análisis de información ecológica |
| Dominio | Biodiversidad, taxonomía e interacciones planta-animal |
| Área inicial | Zona sur de la Reserva de la Biosfera Montes Azules, Chiapas |
| Área comparativa | Ejido Playón de la Gloria, claramente separado del polígono de la reserva |
| Usuarios principales | Estudiantes, docentes, investigadores y administradores de datos |
| Resultado central | Un catálogo navegable y trazable de taxones, interacciones y evidencias |

### 2.1 Problema

La información sobre biodiversidad y sus interacciones se encuentra distribuida entre publicaciones científicas, catálogos taxonómicos, repositorios de ocurrencias y agregadores de relaciones ecológicas. Estas fuentes no describen necesariamente el mismo fenómeno: un registro de presencia documenta que un organismo fue observado o recolectado en un lugar; un estudio de alimentación puede documentar consumo; una cámara trampa puede registrar consumo o remoción de frutos; y una inferencia de dispersión de semillas requiere una interpretación adicional de la evidencia.

Sin una estructura que conserve esas diferencias, el usuario puede confundir coexistencia con interacción, combinar localidades distintas o perder el método y la publicación que justifican una relación. Esto dificulta construir redes ecológicas confiables y comparar estudios.

### 2.2 Objetivo general

Desarrollar una plataforma que integre y permita explorar información taxonómica y relaciones ecológicas documentadas, preservando la procedencia, el contexto espacial y temporal, el método de observación y el nivel de evidencia de cada registro.

### 2.3 Objetivos específicos

1. Reunir referencias taxonómicas y registros de presencia útiles para contextualizar los taxones del dominio.
2. Registrar relaciones planta-animal sustentadas por publicaciones o conjuntos de datos identificables.
3. Permitir la exploración de redes de frugivoría por taxón, localidad, periodo y tipo de evidencia.
4. Mantener separadas las observaciones de presencia y las afirmaciones de interacción.
5. Facilitar la revisión de la evidencia original detrás de cada relación presentada.
6. Demostrar una integración funcional de los modelos relacional, documental y de grafo, cada uno con responsabilidades justificadas.

### 2.4 Usuarios y necesidades

| Usuario | Necesidad principal | Funciones relacionadas |
|---|---|---|
| Estudiante | Comprender ejemplos de interacciones y redes ecológicas | Consultar taxones, explorar conexiones y revisar fuentes |
| Docente | Utilizar datos trazables como material educativo | Mostrar redes por localidad y explicar la evidencia |
| Investigador | Consultar relaciones y comparar estudios sin perder método ni contexto | Filtrar por taxón, localidad, periodo, fuente y evidencia |
| Administrador o curador de datos | Incorporar, revisar y corregir registros con procedencia | Administrar fuentes, importaciones, taxonomía y estado de revisión |

La primera versión no se plantea como un sistema de monitoreo en tiempo real ni como una herramienta oficial de toma de decisiones para el manejo de la reserva.

## 3. Delimitación geográfica y ecológica

### 3.1 Área natural de referencia

La Reserva de la Biosfera Montes Azules se encuentra en Chiapas. La ficha oficial del Sistema de Información, Monitoreo y Evaluación para la Conservación (SIMEC) de la CONANP la identifica como Reserva de la Biosfera, con una superficie reportada de **331,200 hectáreas**, dentro de los municipios de Las Margaritas, Maravilla Tenejapa y Ocosingo. La ficha enumera, entre otros, bosque de coníferas, bosque mesófilo de montaña, pastizal, selva alta perennifolia y vegetación hidrófila. Fuente: [ficha SIMEC de Montes Azules](https://simec.conanp.gob.mx/informacion/ficha/172?reg=11).

Para el proyecto, el polígono oficial de la reserva será la referencia espacial de pertenencia al área protegida. La CONANP publica archivos de polígonos en formato Shapefile; su página de descargas consultada el 20 de noviembre de 2026 lista el conjunto de Áreas Naturales Protegidas con fecha **junio de 2026**. Antes de una carga de datos espaciales se deberá registrar el archivo exacto, su fecha, sistema de coordenadas y metadatos. Fuente: [SIG CONANP — descarga de archivos SHAPE](https://sig.conanp.gob.mx/snd/shape).

### 3.2 Localidades de interés

**Localidad núcleo: sector sur de Montes Azules.** El estudio de Olea-Wagner y colaboradores describe una localidad dentro de la selva alta perennifolia de la zona sur de la reserva. El artículo no permite asignar a cada muestra una coordenada GPS individual; por ello, los datos de ese estudio se asociarán inicialmente a una localidad de estudio de escala regional, no a puntos inventados.

**Localidad comparativa: Ejido Playón de la Gloria (PDLG).** El mismo estudio distingue esta localidad de la zona ubicada dentro de la reserva y la caracteriza como un mosaico con fragmentos de selva, cacaotales, potreros y acahuales. BioLink la tratará como una localidad externa de comparación, no como parte del polígono de Montes Azules.

El artículo estudia ambas localidades y señala que colindan con el río Lacantún. No se debe deducir que todos los taxones o interacciones del artículo ocurrieron en ambas localidades: los valores y descripciones por localidad y temporada deben conservarse tal como aparecen en las tablas y resultados del estudio.

### 3.3 Proceso ecológico focal

La primera versión se limitará a **frugivoría y relaciones asociadas al consumo o remoción de frutos** entre plantas y dos grupos de mamíferos:

- murciélagos frugívoros;
- mamíferos terrestres que consumen o remueven frutos depositados en el suelo del bosque.

Esta delimitación permite reunir dos tipos de evidencia complementarios: semillas identificadas en excretas de murciélagos y registros de cámaras trampa en árboles focales.

### 3.4 Tipos de relación que podrá representar BioLink

| Tipo conceptual | Cuándo se utiliza | Restricción |
|---|---|---|
| `CONSUMES_FRUIT_OF` | La fuente documenta consumo de frutos | Debe indicarse si la evidencia es observación directa o identificación de semillas en excretas |
| `CONSUMES_OR_REMOVES_FRUIT_OF` | La fuente agrupa el comportamiento como consumo o remoción | No separar ambos comportamientos si la fuente no los distingue por registro |
| `SEEDS_FOUND_IN_EXCRETA_OF` | Se identifican semillas de una planta en excretas de un animal | Es evidencia de ingestión y excreción; no demuestra por sí sola germinación o establecimiento |
| `SEED_DISPERSAL_EVIDENCE` | La fuente respalda explícitamente el papel dispersor o la endozoocoria | Debe marcarse la naturaleza de la evidencia y no convertirla en éxito de regeneración |

La visita a un árbol, la presencia de una especie en el área y el cruce frente a una cámara no se registrarán como consumo. Una remoción de fruto tampoco se convertirá automáticamente en dispersión de semillas.

## 4. Investigación documental del dominio

### 4.1 Estudio de murciélagos frugívoros — Olea-Wagner et al. (2007)

**Referencia:** Olea-Wagner, A., Lorenzo, C., Naranjo, E., Ortiz, D. y León-Paniagua, L. (2007). *Diversidad de frutos que consumen tres especies de murciélagos (Chiroptera: Phyllostomidae) en la selva lacandona, Chiapas, México*. Revista Mexicana de Biodiversidad, 78, 191–200. [DOI: 10.22201/ib.20078706e.2007.001.393](https://doi.org/10.22201/ib.20078706e.2007.001.393).

El estudio analiza tres especies de murciélagos frugívoros:

- *Artibeus lituratus*;
- *Carollia perspicillata*;
- *Sturnira lilium*.

Se recolectaron **207 muestras de excretas de 115 individuos** y se identificaron **19 taxones vegetales**. El trabajo se realizó entre enero y julio de 2004 en dos localidades: una en la zona sur de Montes Azules y otra en el Ejido Playón de la Gloria. Las semillas recuperadas de las excretas se utilizaron para describir los frutos consumidos.

El artículo aporta ejemplos de relaciones con contexto espacial y temporal:

- *Artibeus lituratus* presentó frecuencias mayores de consumo de *Cecropia obtusifolia* y *Cecropia peltata* en ambas localidades y durante ambas épocas de muestreo.
- Para *Carollia perspicillata*, las frecuencias mayores de consumo de *Piper auritum* y *Piper hispidum* se reportan durante la época de lluvia dentro de Montes Azules.
- Para *Sturnira lilium*, la mayor frecuencia de consumo de *Piper hispidum* se reporta en Playón de la Gloria en ambas épocas.

El artículo distingue la época seca (enero-marzo) y la época de lluvia (mayo-julio) para el periodo estudiado. Reporta diferencias entre localidades y temporadas; por tanto, la dimensión temporal debe conservarse en los registros y no reducirse a una relación permanente sin contexto.

Los 19 taxones vegetales identificados en el cuadro del artículo son:

1. *Cecropia obtusifolia*;
2. *Cecropia peltata*;
3. *Ficus insipida*;
4. *Ficus* sp.;
5. *Ficus yoponensis*;
6. *Ficus lundelli* (grafía tal como aparece en el cuadro consultado; requiere conciliación taxonómica);
7. *Solanum americanum*;
8. *Solanum torvum*;
9. *Solanum rudepanum* (grafía tal como aparece en el cuadro consultado; requiere conciliación taxonómica);
10. *Solanum ochraceo-frrugineum* (grafía tal como aparece en el cuadro consultado; requiere conciliación taxonómica);
11. *Physalis angulata*;
12. *Capsicum annuum*;
13. *Clidemia* sp.;
14. *Piper hispidum*;
15. *Piper lapathifolium*;
16. *Piper auritum*;
17. *Piper* sp. (morfoespecie 2);
18. *Piper* sp. (morfoespecie 3);
19. *Syzygium jambos*.

Las denominaciones a nivel de género y las morfoespecies deben conservarse como tales. No se deben inventar epítetos específicos. Las grafías dudosas se guardarán como nombre original de la fuente y se reconciliarán en un campo separado cuando exista respaldo taxonómico.

**Interpretación permitida:** encontrar semillas en excretas permite documentar ingestión y excreción, y el artículo discute la función de los murciélagos como dispersores de semillas. **No permite afirmar** que todas las semillas germinaron, que se establecieron plántulas o que se conoce el lugar exacto donde fueron depositadas.

### 4.2 Estudio de mamíferos terrestres — Camargo-Sanabria y Mendoza (2016)

**Referencia:** Camargo-Sanabria, A. A. y Mendoza, E. (2016). *Interactions between terrestrial mammals and the fruits of two neotropical rainforest tree species*. Acta Oecologica, 73, 45–52. [DOI: 10.1016/j.actao.2016.02.005](https://doi.org/10.1016/j.actao.2016.02.005). La tesis doctoral de Camargo-Sanabria (UNAM, 2016) contiene el desarrollo metodológico y tablas del estudio: [Tesis digital UNAM](https://tesiunamdocumentos.dgb.unam.mx/ptd2016/enero/0739385/0739385.pdf).

El estudio se desarrolló en la Reserva de la Biosfera Montes Azules y examinó frutos de dos árboles:

- *Licania platypus*;
- *Pouteria sapota*.

Se monitorearon **13 árboles focales** (nueve de *Licania platypus* y cuatro de *Pouteria sapota*) con cámaras trampa. El esfuerzo acumulado reportado fue de **278 días-cámara**, con aproximadamente **2,500 fotografías agrupadas en 235 eventos**. Se registraron 13 especies de mamíferos; de ocho se obtuvo evidencia de consumo o remoción de frutos.

Las ocho especies con evidencia de interacción con frutos fueron:

- *Conepatus semistriatus*;
- *Cuniculus paca*;
- *Dasyprocta punctata*;
- *Didelphis marsupialis*;
- *Eira barbara*;
- *Nasua narica*;
- *Pecari tajacu*;
- *Tapirus bairdii*.

El artículo informa que el conjunto asociado a *Licania platypus* (seis especies) fue un subconjunto del asociado a *Pouteria sapota* (ocho especies). En la tesis, el comportamiento observado se clasificó como interacción directa cuando los mamíferos consumían o removían frutos; los individuos que únicamente cruzaban frente a la cámara se clasificaron por separado. Esta distinción es importante para BioLink: la mera detección de un mamífero no debe convertirse en una arista de consumo.

La publicación mide visitas e intensidad de interacción, pero el comportamiento agrupado de consumir o remover frutos no siempre permite identificar cuál de las dos acciones ocurrió en cada registro. BioLink conservará el término combinado cuando esa sea la resolución de la fuente. Tampoco se asumirá que toda remoción equivale a dispersión efectiva de semillas.

### 4.3 Síntesis de la evidencia disponible

| Fuente | Taxones focales | Evidencia | Escala temporal | Localidad | Uso previsto |
|---|---|---|---|---|---|
| Olea-Wagner et al. (2007) | 3 murciélagos y 19 taxones vegetales | Semillas identificadas en excretas | Enero-julio de 2004; estaciones seca y lluviosa | Sector sur de Montes Azules y PDLG, separados | Relaciones de frugivoría y evidencia de endozoocoria |
| Camargo-Sanabria y Mendoza (2016) | 8 mamíferos con interacción directa y 2 árboles focales | Cámaras trampa; consumo o remoción de frutos | Muestreo de 2013-2014 | Montes Azules | Relaciones entre mamíferos terrestres y frutos depositados en el suelo |

Estas publicaciones ofrecen un núcleo inicial de evidencia suficiente para definir la aplicación y demostrar que existen relaciones ecológicas documentadas en el área focal. No equivalen a un inventario exhaustivo de la biodiversidad de Montes Azules.

## 5. Fuentes de información y viabilidad documental

La investigación identifica fuentes con responsabilidades diferentes. Ninguna fuente secundaria debe sustituir la evidencia original de una interacción cuando esta se encuentre disponible.

| Fuente | Tipo de información | Aplicación en BioLink | Estado de revisión en esta etapa | Limitaciones que deben conservarse |
|---|---|---|---|---|
| [CONANP — SIMEC Montes Azules](https://simec.conanp.gob.mx/informacion/ficha/172?reg=11) | Datos oficiales del área protegida, superficie, municipios, vegetación y especies representativas | Definir el área geográfica de referencia | Ficha consultada | La ficha general no documenta interacciones específicas |
| [SIG CONANP — SHAPE](https://sig.conanp.gob.mx/snd/shape) | Polígonos oficiales de ANP y metadatos | Determinar si una observación cae dentro o fuera del polígono | Disponibilidad del conjunto verificada; archivo no descargado ni procesado en esta etapa | Se requiere registrar versión exacta, CRS y calidad geométrica antes de cruzar puntos |
| [API EncicloVida v2](https://api.enciclovida.mx/v2/) | Taxones, clasificación, descripciones, medios, registros geográficos y búsqueda por estado, municipio o ANP | Resolver nombres y consultar contexto de especies | Documentación de API verificada; no se reportan conteos de consulta en esta etapa | Los datos de presencia no demuestran interacción; licencia y atribución se revisan por recurso |
| [GBIF Occurrence API](https://techdocs.gbif.org/en/openapi/v1/occurrence) | Registros de presencia con taxonomía, fecha, localidad y coordenadas cuando existen | Enriquecer contexto espacial y temporal de los taxones | Documentación y límites de consulta verificados; no se reportan conteos de consulta en esta etapa | Búsquedas paginadas de hasta 300 resultados por página y límite de 100,000 resultados por búsqueda; para grandes descargas se requiere una solicitud autenticada y asíncrona |
| [GloBI — Data](https://www.globalbioticinteractions.org/data) | Datos de interacciones de múltiples conjuntos publicados | Descubrir relaciones complementarias y sus fuentes originales | Productos, API y descargas versionadas identificados | Cobertura sesgada por región, tiempo y taxonomía; los nombres pueden mapearse con errores; no asumir que un registro está dentro de Montes Azules sin evidencia geográfica |
| Olea-Wagner et al. (2007) | Interacciones entre murciélagos y plantas | Fuente primaria de relaciones locales de frugivoría | Artículo y tablas revisados | Dos localidades distintas; los datos no proporcionan coordenadas individuales para cada muestra |
| Camargo-Sanabria y Mendoza (2016) | Interacciones entre mamíferos terrestres y frutos de dos árboles | Fuente primaria de relaciones dentro de la reserva | Artículo y tesis revisados | La categoría publicada combina consumo o remoción; no debe traducirse automáticamente en dispersión de semillas |

### 5.1 Reglas de uso de las fuentes

1. **CONANP** define el polígono del área protegida y sus datos institucionales; no se utilizará como fuente de interacciones que su ficha no documenta.
2. **EncicloVida y GBIF** se utilizarán para taxonomía y ocurrencias. Una ocurrencia no crea una relación entre dos especies.
3. **GloBI** será una fuente de descubrimiento y enriquecimiento, no una autoridad automática para la presencia de una interacción en Montes Azules. Se debe conservar el dataset de origen, referencia, versión y licencia.
4. Las **publicaciones originales** serán la base para las relaciones incluidas en el núcleo validado. Se guardará la referencia precisa a artículo, tabla, figura, página o sección que respalda cada afirmación.
5. Los datos e imágenes tendrán una política de atribución y licencia por recurso. En GBIF se conservarán las licencias y citas de los conjuntos que contribuyen a una descarga; las descargas y los resultados derivados deben citarse de forma reproducible. Las imágenes no heredan automáticamente la licencia de los datos de ocurrencia.
6. Si posteriormente se incorpora iNaturalist, se revisará por separado la licencia de cada observación y de cada fotografía o audio. Sus coordenadas pueden estar ocultas o desplazadas para taxones sensibles; no se tratarán como coordenadas exactas cuando estén ofuscadas.

### 5.2 Qué se verificó y qué no se afirma

La documentación vigente de EncicloVida confirma que su API ofrece búsquedas de especies por región y consultas de descripciones, clasificaciones, medios y registros. La documentación de GBIF confirma la paginación y los mecanismos de descarga. GloBI publica datos estables versionados y productos de descarga, incluidas representaciones para bases de grafos.

**No se presentan cifras de ocurrencias consultadas en tiempo real para Montes Azules**, porque en esta etapa no se completó una extracción automatizada y reproducible de las APIs ni el cruce contra el polígono oficial. Inventar o estimar esos conteos produciría una línea base no verificable. Esta tarea corresponde a la preparación de adquisición y carga de datos, antes de poblar las bases; no impide cerrar la definición de la aplicación.

## 6. Alcance de la primera versión (V1)

### 6.1 Incluye

- Catálogo de taxones vegetales, murciélagos y mamíferos incluidos en la evidencia revisada.
- Fichas de taxones con nombres originales, nombre aceptado cuando esté validado, clasificación y fuentes.
- Registro de relaciones documentadas de consumo o remoción de frutos y de evidencia de semillas en excretas.
- Metadatos de estudio, método, fecha o periodo, localidad, estación del año y referencia bibliográfica.
- Distinción espacial entre la zona estudiada dentro de Montes Azules y Playón de la Gloria.
- Exploración de relaciones y redes por taxón, localidad, periodo, método y tipo de evidencia.
- Consulta de la fuente que sustenta cada relación.
- Funciones básicas para administrar y revisar fuentes y registros incorporados.
- Indicadores descriptivos de la red (por ejemplo, número de taxones y relaciones documentadas, grado y componentes), siempre acompañados de filtros y advertencias sobre la cobertura de la muestra.
- Simulación educativa de eliminación de un nodo para observar cambios matemáticos en la red; no será presentada como predicción ecológica de extinción ni como pronóstico de efectos reales.

### 6.2 No incluye

- Una red alimentaria completa de la Selva Lacandona.
- Todos los grupos taxonómicos, ecosistemas o tipos de interacción.
- Polinización, parasitismo, depredación, competencia, enfermedades o relaciones humano-fauna.
- Predicción de abundancia, viabilidad poblacional, extinción o regeneración del bosque.
- Monitoreo en tiempo real, sensores o captura ciudadana de observaciones.
- Georreferenciación puntual de muestras cuando la fuente solo proporciona una localidad general.
- Inferir interacciones a partir de la simple coexistencia o de registros de presencia.
- Reproducir artículos completos, fotografías o multimedia sin una licencia o autorización que lo permita.

### 6.3 Criterio de inclusión de un registro

Una relación podrá formar parte de la red principal de BioLink cuando cumpla, como mínimo, con lo siguiente:

1. Identificación de los dos taxones involucrados, al nivel taxonómico realmente respaldado.
2. Tipo de interacción descrito por la fuente, sin elevar el nivel de detalle del comportamiento.
3. Referencia rastreable al estudio, conjunto de datos o registro de origen.
4. Localidad y precisión geográfica expresadas según la fuente; el sistema podrá marcar la pertenencia al ANP como confirmada, externa o indeterminada.
5. Periodo o fecha con el nivel de precisión disponible.
6. Método o tipo de evidencia.
7. Estado de revisión taxonómica y documental.

Si falta la evidencia de interacción, el registro puede conservarse como ocurrencia o contexto, pero no se incorporará como una relación positiva en la red.

## 7. Operaciones principales de la aplicación

La siguiente lista delimita capacidades que serán desarrolladas en detalle como casos de uso durante la etapa 2.

| ID | Operación | Resultado esperado | Modelos que se justifican |
|---|---|---|---|
| OP-01 | Buscar un taxón por nombre científico, nombre común o identificador | Ficha del taxón con clasificación, variantes de nombre y fuentes | Documental + relacional |
| OP-02 | Consultar las interacciones documentadas de un taxón | Relaciones entrantes y salientes con tipo de evidencia y filtros | Grafo + documental |
| OP-03 | Explorar la red de interacción de una localidad | Subred de plantas y animales conectados por relaciones respaldadas | Grafo |
| OP-04 | Comparar Montes Azules con Playón de la Gloria | Comparación descriptiva por localidad, temporada y fuente, sin mezclar sus registros | Grafo + documental + relacional |
| OP-05 | Consultar la evidencia de una relación | Publicación, tabla/figura, método, periodo y metadatos relacionados | Documental + relacional |
| OP-06 | Registrar y revisar una fuente o conjunto de datos | Fuente identificada, estado de importación, validación y trazabilidad | Relacional + documental |
| OP-07 | Analizar conectividad o simular la remoción de un nodo | Indicadores y escenario hipotético de red, con advertencias metodológicas | Grafo |
| OP-08 | Comparar registros de presencia con interacciones documentadas | Vista separada de ocurrencias y de relaciones ecológicas | Documental + grafo |

## 8. Justificación funcional de los tres modelos de bases de datos

La selección se realiza por las operaciones y la naturaleza de los datos, no por preferencia previa por un motor. La selección de tecnologías concretas queda pendiente para la etapa de arquitectura.

### 8.1 Modelo relacional — administración e integridad

Responsabilidad propuesta:

- cuentas, roles y permisos de usuarios;
- proyectos o espacios de trabajo;
- catálogo de fuentes y conjuntos de datos;
- ejecuciones de importación, lotes y estados de revisión;
- identificadores internos estables y correspondencias entre registros;
- registro de validaciones y auditoría de cambios;
- restricciones de unicidad y consistencia para evitar duplicados de control.

**Por qué se necesita:** estas operaciones requieren relaciones estructuradas, claves, restricciones y transacciones. Por ejemplo, una importación no debe marcarse como validada si faltan sus datos de procedencia o si el lote no pasó los controles requeridos. La administración de usuarios y estados tampoco se beneficia de una estructura libre sin restricciones.

### 8.2 Modelo documental — expedientes y datos heterogéneos

Responsabilidad propuesta:

- fichas de taxones con campos opcionales y atributos diferentes según el grupo;
- respuestas o registros originales de las fuentes externas, conservando su estructura de origen;
- expedientes de evidencia con metadatos anidados de método, muestreo, referencia, licencia y notas;
- información descriptiva de estudios que puede variar entre publicaciones.

**Por qué se necesita:** los datos taxonómicos y bibliográficos no tienen siempre el mismo conjunto de atributos. Un murciélago puede tener datos de dieta y refugio; una planta puede tener forma de vida, fenología o categoría sucesional; una fuente puede describir métodos y esfuerzos de muestreo que otra no reporta. Un modelo documental permite conservar esos perfiles y estructuras variables sin forzar todos los campos en una única forma rígida.

### 8.3 Modelo de grafo — exploración de relaciones ecológicas

Responsabilidad propuesta:

- nodos para taxones, localidades y estudios;
- relaciones dirigidas o tipadas para representar las interacciones documentadas;
- propiedades de relación para método, periodo, localidad, frecuencia, fuente y clase de evidencia;
- recorridos y patrones de conexión entre plantas, mamíferos y localidades.

**Por qué se necesita:** el valor principal de BioLink no es solamente buscar un registro aislado, sino responder preguntas de conectividad: qué animales tienen relaciones documentadas con una planta, qué plantas comparten frugívoros, qué taxones conectan distintas partes de la red y cómo cambia la estructura de una subred al filtrar por localidad o periodo. El modelo de grafo representa esas conexiones como elementos centrales y permite recorrerlas directamente.

### 8.4 Matriz de responsabilidades

| Aspecto | Relacional | Documental | Grafo |
|---|---|---|---|
| Responsabilidad principal | Control, integridad, usuarios, fuentes y procesos | Fichas y expedientes flexibles | Red de taxones e interacciones |
| Estructura | Tablas, claves y restricciones | Documentos y estructuras anidadas | Nodos, relaciones y propiedades |
| Operación distintiva | Crear/actualizar con integridad y auditar | Consultar o actualizar expedientes variables | Recorrer relaciones y encontrar patrones |
| Ejemplo BioLink | Validar un lote de importación | Abrir la ficha documental de un taxón | Consultar todos los frugívoros conectados a una planta |
| Prueba principal | Unicidad, integridad referencial y transacciones | Validación de documentos y consultas | Cardinalidades, recorridos y resultados de red |

### 8.5 Fuente de verdad y sincronización inicial

- La **publicación científica o conjunto original** es la fuente de autoridad de la evidencia ecológica.
- El **modelo relacional** será responsable de los identificadores internos, el estado de revisión, la propiedad de fuentes y los procesos de importación.
- El **modelo documental** conservará el contenido estructurado de origen permitido por su licencia y los expedientes descriptivos; no sustituirá la publicación original.
- El **grafo** contendrá la proyección de las relaciones aceptadas para consulta de redes. Una relación no validada no debe entrar en la red principal.
- Los tres modelos compartirán identificadores de referencia; no se copiarán indiscriminadamente los mismos datos completos a las tres bases.
- Si una operación actualiza más de una base, el backend deberá registrar el resultado de cada paso y prever reintento o reconciliación. No se declarará éxito total si una escritura parcial falla.

Estas son responsabilidades conceptuales. La estructura física, los motores concretos, los índices y el mecanismo de sincronización se definirán en las etapas correspondientes.

## 9. Principios de calidad, trazabilidad y taxonomía

1. **Nombre original y nombre reconciliado separados.** Se conservará literalmente el nombre de la fuente. La correspondencia con un nombre aceptado será un dato adicional, con autoridad taxonómica, fecha de consulta y nivel de confianza.
2. **Resolución taxonómica honesta.** *Ficus* sp., *Clidemia* sp. y las dos morfoespecies de *Piper* permanecerán a nivel de género/morfoespecie hasta que exista evidencia para resolverlas.
3. **Ocurrencia no es interacción.** Que dos especies tengan registros en la misma reserva no autoriza a crear una relación ecológica entre ellas.
4. **La ausencia de registro no es prueba de ausencia.** Una cámara que no captó interacción o una base que no contiene una relación no demuestra que nunca ocurra.
5. **Método conservado.** Semillas en excretas y cámaras trampa son evidencias diferentes y no se fusionarán bajo una etiqueta genérica sin conservar el método.
6. **Comportamiento según la fuente.** Si el artículo combina consumo y remoción, BioLink conservará la categoría combinada.
7. **Localidad y periodo no se extrapolan.** No se asignarán coordenadas, fechas exactas o pertenencia al polígono cuando la fuente no lo respalde.
8. **Referencia a nivel de afirmación.** Cada arista de la red deberá poder rastrearse hasta su estudio, conjunto de datos y ubicación interna (tabla, figura, página o registro), cuando estén disponibles.
9. **Licencia por recurso.** Las licencias de datos, texto, imagen y audio se tratarán por separado.
10. **Versionado de conjuntos.** Para una importación reproducible se registrarán fecha de consulta, versión, endpoint o consulta, filtros, licencia y cita del conjunto utilizado.

## 10. Riesgos y medidas de control

| Riesgo | Efecto posible | Medida prevista |
|---|---|---|
| Sesgo geográfico, temporal o taxonómico de los repositorios | La red puede representar mejor las zonas o grupos más estudiados | Mostrar fuente, periodo, método y cobertura; no interpretar el volumen de datos como abundancia real |
| Sinónimos, grafías distintas o identificaciones incompletas | Duplicación o unión errónea de taxones | Guardar nombre original y reconciliar mediante identificadores externos y revisión |
| Coordenadas ausentes o generalizadas | Asignación incorrecta dentro/fuera del ANP | Usar niveles de precisión y estados confirmada/externa/indeterminada |
| Mezcla de Montes Azules y Playón de la Gloria | Comparación geográfica inválida | Mantener localidades y estatus de protección separados |
| Consumo/remoción interpretados como dispersión | Sobreestimación del papel ecológico | Conservar el tipo de evidencia y separar inferencia de observación |
| Diferentes periodos y métodos | Comparaciones no equivalentes | Exigir filtro por fecha, temporada, método y fuente |
| Licencias heterogéneas | Reutilización no permitida de datos o multimedia | Registrar licencia y atribución por dataset/medio; no almacenar medios sin autorización |
| Falta de datos masivos ya descargados | No es posible afirmar volúmenes actuales de datos disponibles | Ejecutar extracción y conteo reproducible antes de poblar las bases |

## 11. Prueba de suficiencia de la propuesta

La aplicación satisface la prueba de suficiencia planteada por la guía del proyecto:

- **Relacional:** una operación de administración y revisión de importaciones debe mantener integridad entre usuarios, fuentes, lotes, registros y estados; además, debe permitir auditoría de las validaciones.
- **Documental:** la ficha de un taxón y el expediente de un estudio contienen estructuras variables y anidadas que dependen del grupo biológico y del método utilizado.
- **Grafo:** explorar la red de frugivoría, identificar taxones compartidos y comparar subredes por localidad requiere recorrer relaciones explícitas y sus patrones de conexión.

Eliminar cualquiera de los modelos deterioraría una capacidad sustancial: sin relacional se debilita el control y la integridad del flujo de datos; sin documental se fuerza la heterogeneidad a estructuras rígidas o se pierden los expedientes originales; sin grafo, las consultas de conectividad se convierten en uniones repetidas sobre datos tabulares sin representar la red como estructura principal.

## 12. Criterios de aceptación de la etapa 1

| Criterio de la guía | Resultado |
|---|---|
| Nombre y descripción de la aplicación | Definidos |
| Problema concreto | Definido |
| Usuarios identificables y necesidades | Definidos |
| Objetivo general | Definido |
| Alcance y exclusiones | Delimitados |
| Operaciones principales | Identificadas y clasificadas |
| Datos y dominio requeridos | Delimitados a taxones, interacciones, estudios, evidencia y localidades |
| Justificación de los tres modelos | Justificada mediante operaciones distintas |
| Fuentes científicas del dominio | Dos estudios locales revisados y citados |
| Fuentes institucionales y repositorios | CONANP, EncicloVida, GBIF y GloBI documentados |
| Riesgos y reglas de trazabilidad | Definidos |

**Dictamen:** la **Etapa 1 está completada** como propuesta de aplicación e investigación documental del dominio. La aplicación está suficientemente delimitada para pasar al modelado de requisitos de la etapa 2.

La extracción masiva de registros desde EncicloVida, GBIF o GloBI, el conteo de ocurrencias dentro del polígono oficial y la reconciliación completa de nombres son actividades de adquisición y preparación de datos. No se presentan como resultados realizados ni como condiciones para fingir que existe un volumen de datos ya descargado. Deberán hacerse antes de la carga de las bases y con consultas reproducibles.

## 13. Entrada a la etapa 2

La siguiente etapa deberá convertir esta propuesta en requisitos verificables. Sus entregables serán:

1. actores y casos de uso detallados;
2. requisitos funcionales y no funcionales;
3. reglas del dominio y validaciones;
4. catálogo de operaciones con entradas, salidas, errores y modelos participantes;
5. matriz inicial de responsabilidades y datos fuente de verdad, ampliada a nivel de entidad;
6. escenarios de aceptación para consultas aisladas e integradas.

No se debe crear todavía el esquema físico de las bases, elegir definitivamente los motores ni comenzar la programación de persistencia. Esas decisiones dependerán del catálogo de operaciones ya validado.

---

## Referencias

1. Comisión Nacional de Áreas Naturales Protegidas (CONANP). (s. f.). *Ficha SIMEC: Montes Azules*. https://simec.conanp.gob.mx/informacion/ficha/172?reg=11
2. Comisión Nacional de Áreas Naturales Protegidas (CONANP). (2026). *Descarga de archivos SHAPE: Áreas Naturales Protegidas, junio de 2026*. https://sig.conanp.gob.mx/snd/shape
3. Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO). (s. f.). *EncicloVida API v2*. https://api.enciclovida.mx/v2/
4. GBIF Secretariat. (s. f.). *Occurrence API — Technical Documentation*. https://techdocs.gbif.org/en/openapi/v1/occurrence
5. GBIF Secretariat. (s. f.). *API Downloads*. https://techdocs.gbif.org/en/data-use/api-downloads
6. GBIF Secretariat. (s. f.). *Citation guidelines*. https://www.gbif.org/citation-guidelines
7. Jorrit H. Poelen, James D. Simons y Chris J. Mungall. (2014). *Global Biotic Interactions: An open infrastructure to share and analyze species-interaction datasets*. Ecological Informatics. https://doi.org/10.1016/j.ecoinf.2014.08.005
8. Global Biotic Interactions (GloBI). (s. f.). *Data*. https://www.globalbioticinteractions.org/data
9. Global Biotic Interactions (GloBI). (s. f.). *Data Integration Process*. https://www.globalbioticinteractions.org/process.html
10. Olea-Wagner, A., Lorenzo, C., Naranjo, E., Ortiz, D. y León-Paniagua, L. (2007). *Diversidad de frutos que consumen tres especies de murciélagos (Chiroptera: Phyllostomidae) en la selva lacandona, Chiapas, México*. Revista Mexicana de Biodiversidad, 78, 191–200. https://doi.org/10.22201/ib.20078706e.2007.001.393
11. Camargo-Sanabria, A. A. (2016). *Relevancia ecológica de las interacciones planta-mamífero para la diversidad del bosque húmedo tropical* [Tesis doctoral, Universidad Nacional Autónoma de México]. https://tesiunamdocumentos.dgb.unam.mx/ptd2016/enero/0739385/0739385.pdf
12. Camargo-Sanabria, A. A. y Mendoza, E. (2016). *Interactions between terrestrial mammals and the fruits of two neotropical rainforest tree species*. Acta Oecologica, 73, 45–52. https://doi.org/10.1016/j.actao.2016.02.005
13. Universidad Politécnica de Chiapas. (2026). *Guía de trabajo para estudiantes: Proyecto final — Diseño, desarrollo e integración de tres modelos de bases de datos* [Material de orientación del proyecto].

**Fecha de consulta de fuentes web:** 20 de noviembre de 2026.
