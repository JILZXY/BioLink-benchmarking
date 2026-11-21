# BioLink — Entorno Independiente de Benchmarking (`biolink-benchmarking`)

**Versión:** 1.0  
**Fecha:** 20 de noviembre de 2026  
**Estado:** Arquitectura y protocolo documentados; implementación del entorno de benchmark en progreso independiente; campaña completa de 120 minutos **no ejecutada todavía**.

---

## 1. Propósito e independencia arquitectónica

`biolink-benchmarking` es un **repositorio independiente** diseñado para evaluar empíricamente los seis motores candidatos de BioLink mediante **conexiones directas** desde Python hacia cada motor, utilizando sus controladores, protocolos o interfaces nativas.

### Principio de aislamiento estricto
- El objetivo del benchmark es **medir el comportamiento real de cada base de datos** bajo las cargas y restricciones del proyecto, no medir el rendimiento de una capa web ni de un ORM.
- **Está prohibido** utilizar `biolink-backend`, endpoints FastAPI, servicios de aplicación, repositorios de la aplicación o un ORM compartido como intermediario entre el benchmark y los motores.
- `biolink-benchmarking` mantiene su propio `pyproject.toml`, sus propios scripts, sus propios datasets y su propio `docker/compose.yaml`, sin ninguna dependencia hacia `biolink-backend` ni `biolink-frontend`.

---

## 2. Motores candidatos y conectividad directa

Cada motor candidato se compara **únicamente contra el otro candidato de su mismo modelo de datos**, bajo cargas lógicas equivalentes.

| Modelo | Candidato A | Candidato B | Controlador / protocolo directo | Regla de comparación |
|---|---|---|---|---|
| **Relacional** | MySQL 8.4 LTS *(ref. 8.4.12)* | PostgreSQL 18.7 | MySQL: conector nativo de Python.<br>PostgreSQL: `psycopg`. | MySQL es candidato de primera clase; ambos ejecutan cargas SQL/transaccionales lógicamente equivalentes. |
| **Documental** | MongoDB Community Server 8.0 *(ref. 8.0.38)* | Apache CouchDB 3.5.3 | MongoDB: `pymongo`.<br>CouchDB: interfaz HTTP nativa del motor. | El uso de HTTP para CouchDB corresponde a su interfaz nativa propia, nunca a una API de BioLink. |
| **Grafo** | Neo4j Community *(versión estable fijada + digest)* | Memgraph Community *(versión estable fijada + digest)* | Neo4j: driver oficial de Python (Bolt).<br>Memgraph: cliente compatible mediante protocolo Bolt. | Ambos ejecutan recorridos y upserts equivalentes sobre la proyección `Taxon`–`InteractionAssertion`. |

### Reglas de versionado y comparación
- **Prohibido usar `latest`** en cualquier imagen Docker de experimento.
- Para Neo4j y Memgraph se fijan tags estables concretos al ejecutar y se registra la versión exacta y el digest de la imagen en los metadatos de cada corrida.
- **No se comparan tiempos absolutos entre paradigmas** (por ejemplo, una consulta SQL frente a un recorrido en grafo).
- Se preservan las observaciones de licencia (por ejemplo, SSPL de MongoDB Community frente a Apache 2.0 de CouchDB) y los requisitos de memoria documentados en [03_matriz_comparativa_motores_biolink.csv](./03_matriz_comparativa_motores_biolink.csv).

---

## 3. Estrategia de datos de prueba

El entorno mantiene dos grupos de datos físicamente y lógicamente separados:

### 3.1 Fixture científico de referencia
- Derivado exclusivamente de las evidencias documentadas en la Etapa 1 ([01_etapa_1_biolink.md](./01_etapa_1_biolink.md) y [01_matriz_evidencias_biolink.csv](./01_matriz_evidencias_biolink.csv)): Olea-Wagner et al. (2007) y Camargo-Sanabria y Mendoza (2016).
- Conserva de forma obligatoria: identificador de fuente (`BAT2007`, `MAMMAL2016`), localizador de evidencia, taxones reportados (incluyendo identificaciones a nivel de género o morfoespecie como `Ficus sp.` o `Piper sp.`), tipo de interacción reportado (`CONSUMES_FRUIT_OF`, `CONSUMES_OR_REMOVES_FRUIT_OF`), método, localidad, periodo y limitaciones de interpretación.
- **Reglas inviolables:** no agregar especies ni interacciones inventadas; una ocurrencia o presencia nunca se convierte automáticamente en interacción; **Montes Azules y Playón de la Gloria se mantienen separados**.

### 3.2 Dataset sintético reproducible (`SYNTHETIC_BENCHMARK`)
- Producido por un generador determinista con **semilla configurable**.
- Escalabilidad prevista en tres volúmenes de prueba: **1,000**, **10,000** y **50,000** afirmaciones sintéticas.
- Identificación explícita de todos los registros generados como `SYNTHETIC_BENCHMARK`, sin reutilizar nombres científicos reales de los estudios para entidades ficticias.
- Genera entidades coherentes entre modelos (taxones animales y vegetales sintéticos, localidades, fuentes, evidencias y afirmaciones con relaciones válidas) entregando la **misma información lógica** a ambos candidatos de una misma categoría.
- Genera un archivo **manifiesto** por conjunto con: semilla, volumen objetivo, fecha de generación, parámetros, conteos por entidad, versión del generador y hash/checksum de los archivos producidos.

---

## 4. Workloads derivados del catálogo de BioLink (`OP-01`–`OP-15`)

Cada modelo ejecuta cuatro workloads representativos derivados de [02_catalogo_operaciones_biolink.csv](./02_catalogo_operaciones_biolink.csv). Las consultas pueden usar sintaxis e índices idiomáticos de cada motor sin alterar la semántica ni el modelo lógico.

| Modelo | Workload | Operaciones origen | Descripción funcional medida |
|---|---|---|---|
| **Relacional** (MySQL vs. PostgreSQL) | R1 | `OP-01` | Búsqueda taxonómica por nombre aceptado, nombre original o sinónimo. |
| | R2 | `OP-03`, `OP-05` | Consulta filtrada de afirmaciones por localidad, periodo y estado (`PUBLISHED`). |
| | R3 | `OP-11`, `OP-12` | Inserción transaccional de una afirmación con evidencia, evento de auditoría y registro outbox. |
| | R4 | `OP-09`, `OP-10` | Inserción por lotes de registros de importación y metadatos de validación. |
| **Documental** (MongoDB vs. CouchDB) | D1 | `OP-02` | Lectura de `taxon_dossier` por `taxon_id`. |
| | D2 | `OP-02`, `OP-13` | Consulta por atributos anidados (secciones ecológicas, afirmaciones descriptivas o referencias de fuente). |
| | D3 | `OP-13` | Escritura de una nueva versión de una ficha conservando historial/versión previa. |
| | D4 | `OP-09`, `OP-10` | Inserción masiva de documentos `raw_source_record` originales. |
| **Grafo** (Neo4j vs. Memgraph) | G1 | `OP-03` | Consulta de vecinos de un taxón (`Taxon`–`InteractionAssertion`–`Taxon`) solo sobre afirmaciones `PUBLISHED`. |
| | G2 | `OP-05` | Consulta de subgrafo filtrado por localidad, tipo de interacción y periodo (sin mezclar Montes Azules y PDLG). |
| | G3 | `OP-07` | Conteo de taxones contraparte distintos (grado descriptivo documentado). |
| | G4 | `OP-12` | Upsert idempotente de una afirmación publicada usando `assertion_id`. |

---

## 5. Protocolo de medición, recursos y reglas de decisión

### 5.1 Métricas obligatorias
Para cada corrida y operación medida por separado:
- Latencia individual por operación (`ms`), mediana (`p50`), `p95` y tiempo máximo.
- Operaciones por segundo (`ops/s`) cuando corresponda.
- Tiempo de carga inicial, tiempo de inserción por lote y tiempo de creación de índices (separados de las consultas).
- Almacenamiento ocupado en volumen/disco.
- Pico de memoria del contenedor y uso de CPU durante carga y consultas.
- Errores, timeouts y porcentaje de operaciones correctas (validando IDs, conteos y filtros esperados).

### 5.2 Reglas de ejecución y reproducibilidad
1. Establecer la conexión **antes** de iniciar el cronómetro; la conexión no se mezcla con la latencia de consulta.
2. Ejecutar una fase de calentamiento previa a las iteraciones medidas.
3. Medir cada operación por separado con parámetros equivalentes; **no** usar mezclas arbitrarias de lectura/escritura (como 80/20).
4. Validar obligatoriamente la corrección del resultado devuelto; una consulta más rápida con resultados incorrectos se descarta como ganadora.
5. Exportar metadatos de ejecución en **JSON** (motor, versión exacta, digest, semilla, límites, parámetros) y mediciones individuales en **CSV**, con identificador único y timestamp para **no sobrescribir corridas previas**.

### 5.3 Presupuesto de recursos y campaña completa (máximo 120 minutos)
- **Límites de contenedor:** Relacional `768 MB` | Documental `768 MB` | Grafo `1,024 MB` | Techo global del entorno: `4 GB`.
- **Ejecución secuencial:** un solo candidato levantado a la vez, con limpieza de volumen entre candidatos.
- **Ventana máxima futura de campaña:**
  - Preparación y verificación: `10 min`
  - Relacional (MySQL y PostgreSQL secuenciales): `30 min`
  - Documental (MongoDB y CouchDB secuenciales): `25 min`
  - Grafo (Neo4j y Memgraph secuenciales): `35 min`
  - Validación, consolidación y exportación de reportes: `20 min`
  - **Total máximo:** `120 min`

### 5.4 Criterio de decisión final (post-benchmark)
Conforme a la sección 9.7 de [03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md](./03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md), la selección final por paradigma priorizará en orden:
1. Cumplimiento funcional y corrección de resultados.
2. Integridad, trazabilidad y capacidad de reconstrucción.
3. Capacidad para ejecutar las operaciones con los volúmenes objetivo.
4. Estabilidad y pico de memoria dentro del presupuesto de 4 GB.
5. Latencias `p50`/`p95` y tiempos de carga.
6. Simplicidad operativa, calidad de drivers y licencia.

---

## 6. Estado actual y observaciones pendientes

- **Estado de ejecución:** No se ha ejecutado todavía la campaña completa de 120 minutos ni existe un ganador definitivo por modelo; las pruebas de etapa inicial se limitan a validaciones breves de configuración, arranque, salud, conexión directa, inserción/consulta/limpieza de humo.
- **Preservación del trabajo en desarrollo:** Esta actualización documental no modifica drivers, workloads, scripts, configuraciones Docker ni límites de recursos del entorno de benchmarking que se encuentra en desarrollo.
- **Puntos pendientes a verificar al consolidar el repositorio `biolink-benchmarking`:**
  1. Confirmar la fijación de tags exactos y digests SHA256 para **Neo4j Community** y **Memgraph Community** al momento de descargar y validar las imágenes.
  2. Asegurar que el repositorio raíz de `biolink-benchmarking` no incluya carpetas obsoletas de aplicación (`backend/`, `api/`, `frontend/`) ni dependencias hacia `biolink-backend`.
  3. Verificar que el fixture científico de `biolink-benchmarking` derive con trazabilidad verificable de [01_matriz_evidencias_biolink.csv](./01_matriz_evidencias_biolink.csv).
