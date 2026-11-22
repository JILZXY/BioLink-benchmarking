# Limitaciones Experimentales, Fallos e Interpretación Crítica (`03_limitaciones_benchmarking.md`)

**Fecha de corte:** 21 de noviembre de 2026  
**Propósito:** Registrar con rigor académico todas las limitaciones de diseño, asimetrías de código entre adaptadores, fallos observados, métricas no comparables y alcance real de validez de las conclusiones obtenidas en `biolink-benchmarking`.

---

## 1. Métricas de Almacenamiento No Comparables (`storage_bytes`)

El campo `storage_bytes` registrado en `results/summaries/*.json` y en las tablas de reportes comparativos **no mide un concepto físico equivalente entre motores**. Usar estos valores para afirmar que un motor ocupa más o menos disco que otro sería metodológicamente incorrecto:

| Motor | Implementación real en `src/biolink_bench/drivers/` | Qué mide en realidad | Valores anómalos observados en Fase 2 (`1k` → `10k` → `50k`) |
|---|---|---|---|
| **Neo4j** | `neo4j_adapter.py:334-338`: `MATCH (n) RETURN count(n) AS nodes` | **Cantidad de nodos** en el grafo, **no bytes**. | `1,950` → `18,332` → `86,428` nodos (reportado en columna `Almacenamiento (bytes)` de los reportes Markdown). |
| **Memgraph** | `memgraph_adapter.py:340-367`: `SHOW STORAGE INFO;` → clave `memory_tracked` | **Bytes asignados en memoria RAM** por el motor *in-memory*, no uso físico de disco. | `109,156,761 B` (`1k`) → `98,283,028 B` (`10k`) → `154,843,217 B` (`50k`), mostrando inversión entre `1k` y `10k` por gestión interna de arenas de memoria. |
| **MySQL** | `mysql_adapter.py:669-684`: `SUM(data_length + index_length)` en `information_schema.TABLES` | **Estimación estadística cacheada** de InnoDB sin `ANALYZE TABLE` previo (actualizada de forma asíncrona). | `2,031,616 B` (`1k`) → **`1,736,704 B` (`10k`)** → `57,638,912 B` (`50k`), con inversión ilógica entre `1k` y `10k` pese a multiplicar 10× las filas. |
| **PostgreSQL** | `postgresql_adapter.py:604-609`: `pg_database_size(current_database())` | **Bytes reales en disco** de toda la base de datos, incluyendo ~`8.54 MB` de catálogo del sistema base medidos ya en `smoke` (`8,541,887 B`). | `10,991,295 B` (`1k`) → `23,049,919 B` (`10k`) → `70,915,775 B` (`50k`). |
| **MongoDB** | `mongodb_adapter.py:218-221`: `db.command("dbStats")` → `storageSize + indexSize` | Espacio comprimido asignado por WiredTiger; afectado por *checkpoints* diferidos en corridas de corta duración (`9 s`). | `122,880 B` (`1k`) → `229,376 B` (`10k`) → `8,060,928 B` (`50k`). |
| **CouchDB** | `couchdb_adapter.py:247-255`: suma de `sizes.active` (o `sizes.file`) en las 4 bases | Bytes lógicos activos de árboles B+ de documentos sin incluir fragmentación de disco ni archivos de índices/vistas sin compactar. | `2,067,380 B` (`1k`) → `9,976,076 B` (`10k`) → `40,487,769 B` (`50k`). |

---

## 2. Registro Completo de Fallos Experimentales y su Efecto en la Interpretación

### 2.1 Fallo en Fase 1 — `20261121T014334Z_smoke_memgraph_3b7eb4`
- **Causa exacta (`results/logs/20261121T014334Z_smoke_memgraph_3b7eb4.log`):** `KeyError: 'name'` al ejecutar `get_storage_bytes()` tras `SMOKE_CRUD`, debido a que Memgraph `3.14.0` devuelve las columnas `'storage info'` y `'value'` en `SHOW STORAGE INFO;` en lugar de `'name'`.
- **Efecto en la interpretación:** la prueba funcional de conectividad y CRUD (`SMOKE_CRUD`: `36.49 ms`, `ok=True`, `valid=True`) sí había concluido, pero la metadata del motor quedó incompleta (`server_version="unknown"`, `storage_bytes=None`). Fue corregido antes de repetir exitosamente la corrida `20261121T014458Z_smoke_memgraph_dae560` y no afectó a las corridas de Fase 2.

### 2.2 Fallo en Fase 2 — `20261121T044507Z_bench_neo4j_a63d11` (`50,000` afirmaciones)
- **Causa exacta (`results/logs/20261121T044507Z_bench_neo4j_a63d11.log:9`):** durante la fase `cleanup_test_data`, la sentencia Cypher `MATCH (n {dataset_tag: $tag}) WITH n LIMIT 2000 DETACH DELETE n` excedió el pool de memoria transaccional interno de Neo4j:  
  `TransientError: Neo.TransientError.General.MemoryPoolOutOfMemoryError — The allocation of an extra 2.0 MiB would use more than the limit 268.8 MiB. Currently using 267.0 MiB. dbms.memory.transaction.total.max threshold reached`.
- **Estado de las mediciones de consulta/escritura:** el fallo ocurrió **después** de haber completado la carga (`13,839.91 ms`), la indexación (`55.44 ms`), la captura de nodos (`86,428`) y todas las `140` ejecuciones de `G1`–`G4` (`100.00%` corrección, `0` errores durante los workloads, `OOMKilled: False`).
- **Efecto en la interpretación:**
  1. Las latencias de `G1`–`G4` a `50k` en Neo4j **son válidas**, pero `cleanup_ms = 0.0` quedó no medido por interrupción de la limpieza.
  2. El contenedor alcanzó **`934.20 MiB`** (`91.2%` del límite de `1,024 MiB`), demostrando que Neo4j Community operó muy cerca de la saturación de memoria y que **sin ajuste explícito de parámetros transaccionales ni reducción del tamaño de lote (`<= 1,000` nodos)** falla en eliminaciones o reconciliaciones masivas bajo `1 GiB`.

---

## 3. Asimetrías de Implementación, Indexación y Configuración entre Candidatos

1. **Asimetría de índices previos a carga en Grafos (explica el `954.98 s` de Memgraph en `50k`):**
   - En `neo4j_adapter.py:72-76`, `prepare_schema()` crea 5 restricciones `UNIQUE` que **automáticamente crean índices de búsqueda** antes de ejecutar `load_dataset()`. Así, los `MATCH (a:Taxon {taxon_id: ...})` y `MERGE (a:InteractionAssertion ...)` en bloques de 500 filas durante la carga usan acceso indexado $O(1)/\log N$.
   - En `memgraph_adapter.py:75-83` y `193-201`, las restricciones `UNIQUE` **no habilitan búsqueda por índice**, sino que `CREATE INDEX ON :Taxon(taxon_id);` se difirió a `create_indexes()` **después** de cargar los `42,523` nodos `InteractionAssertion` y `42,523` nodos `Evidence`. En consecuencia, `load_dataset()` realizó escaneos lineales acumulativos ($O(N^2)$), disparando la carga de `0.65 s` (`1k`) → `40.41 s` (`10k`) → **`954.98 s` (`50k`)**. Además, `MEMGRAPH_INDEXES` omitió índices para `:Evidence(evidence_id)`, `:Source(source_id)`, `interaction_type_code` y `period_start`.
   - **Impacto:** no es válido atribuir la ventaja `69×` en tiempo de carga de Neo4j únicamente al motor; parte sustancial proviene de esta asimetría del adaptador del benchmark.
2. **Desfase de configuración en MySQL (`my.cnf` ignorado en Windows Docker Desktop):**
   - `docker/relational/mysql/my.cnf` especificaba `innodb_buffer_pool_size=256M`, pero `engine_info` en todas las corridas confirmó `innodb_buffer_pool_size_bytes = 134,217,728` (**128 MiB**) porque el sistema de archivos montado desde Windows exponía permisos *world-writable* (`docs/engine_matrix.md:38`). Mientras tanto, PostgreSQL sí recibió `shared_buffers=192MB` por argumentos CLI en `compose.yaml:53-54`.
3. **Asimetría de índice sobre arreglos anidados en Documental (`D2_nested_attribute_query`):**
   - `mongodb_adapter.py:112-115` creó un índice multikey compuesto específico (`idx_claims_nested` sobre `(dataset_tag, claims.field, claims.value)`).
   - `couchdb_adapter.py:116-129` no creó un índice Mango equivalente para los elementos de `claims`. Como muestra `results/raw/20261121T044412Z_bench_couchdb_c198d9.csv`, las consultas de CouchDB para `SYN_DIET_FRUGIVORE` y `SYN_DIET_MIXED_FRUIT` tardaban ~`10`–`12 ms`, pero la 3.ª consulta (`SYN_PRODUCER`, presente en los 800 taxones vegetales almacenados después de los 500 animales) saltaba a **`61`–`67 ms`** (`p95 = 66.207 ms`), evidenciando escaneo `_all_docs`.
4. **Falta de índices FK y `ANALYZE` post-carga en PostgreSQL:**
   - Explica dos hallazgos negativos de PostgreSQL en `50k`: la caída de `R2` (`p50 = 6.727 ms` vs `1.746 ms` en MySQL) por falta de `assertion_id` en el índice y ausencia de `ANALYZE`, y la lentitud de `cleanup_ms = 88,953.18 ms` frente a `3,974.51 ms` de MySQL por carecer de índices en columnas FK hijas (`assertion_evidence`, `review_event`, `outbox_event`).
   - Las optimizaciones implementadas posteriormente en `biolink-backend/database/postgresql/migrations/002_create_indexes.sql` (`idx_assertion_published_r2_covering`) **no han sido medidas todavía dentro de `biolink-benchmarking`**.
5. **Predicados Cypher con disyunción `OR` en `G1` y `G3`:**
   - Tanto `neo4j_adapter.py` como `memgraph_adapter.py` filtraron `WHERE a.status = 'PUBLISHED' AND (actor.taxon_id = $taxon_id OR target.taxon_id = $taxon_id)` con doble `MATCH`, lo cual incrementa el costo de expansión al crecer el grado promedio por taxón (`42,523` aristas repartidas entre `1,300` taxones = ~`65` interacciones por taxón en `50k` frente a ~`13` en `10k`).

---

## 4. Limitaciones del Generador Sintético y de la Cobertura Funcional

1. **Estancamiento de cardinalidad en `taxa` y `taxon_dossiers` entre `10,000` y `50,000`:**
   - `synthetic_generator.py:68-70` impone topes fijos (`500` animales, `800` plantas, `40` fuentes y `6` localidades). En consecuencia, el conjunto de `10k` y el de `50k` tienen exactamente los mismos **`1,300` taxones**, **`2,600` nombres** y **`1,300` expedientes `taxon_dossiers`**.
   - Por esta razón, los workloads **`R1_taxon_search`**, **`D1_read_taxon_dossier`**, **`D2_nested_attribute_query`** y **`D3_versioned_dossier_update`** no miden verdadero escalamiento de su colección o tabla principal al pasar de `10,000` a `50,000` afirmaciones.
2. **Operaciones del catálogo `OP-01`–`OP-15` no medidas directamente como workloads aislados:**
   - Según `docs/workloads.md:48-64`, `OP-04` (ensamble completo multi-motor de evidencia y estudio), `OP-06` (comparación entre dos localidades), `OP-08` (lectura de `study_dossier` + `source_version`), `OP-14` (reconstrucción de auditoría) y `OP-15` (`occurrence` independiente) no cuentan con operaciones cronometradas independientes en `biolink-benchmarking`.
3. **Ausencia de evaluación del flujo de publicación completo en bucle cerrado:**
   - Se midió por separado `R3_transactional_assertion_outbox` (escritura de `outbox_event` en SQL) y `G4_idempotent_assertion_upsert` (proyección Cypher en grafo), pero **no** la latencia extremo a extremo del worker `OutboxProjectionWorker` ni la sincronización optimista de `OP-13` entre PostgreSQL y MongoDB.

---

## 5. Limitaciones Metodológicas, de Monitoreo y de Validez Externa

1. **Concurrencia igual a 1 (`concurrency = 1`):** el cliente Python ejecutó todas las iteraciones de forma secuencial monohilo (`benchmark_runner.py`). Por ello, `ops_per_sec` representa únicamente el recíproco de la latencia media secuencial (`1000 / mean_ms`) y **no refleja contención de bloqueos transaccionales, agotamiento de pools de conexiones ni degradación bajo múltiples usuarios concurrentes** (por ejemplo, el comportamiento de bloqueos a nivel de base o documento en CouchDB frente a MVCC en PostgreSQL/MongoDB).
2. **Tamaño muestral y falta de aleatorización:** cada volumen evaluó solo `n = 30` iteraciones medidas (precedidas de `5` de calentamiento) en una única corrida por motor con semilla fija `20261120` y en orden fijo `10,000 → 1,000 → 50,000`. Un `n = 30` con una sola repetición aporta una caracterización exploratoria sólida, pero es sensible a ruido ocasional del planificador WSL2/Windows (por ejemplo, picos aislados `max_ms` de `20.6 ms` en Memgraph `G3` a `1k` o `14.5 ms` en CouchDB `D1` a `50k`).
3. **Muestreo discreto de recursos (`0.5 s`):** en ejecuciones sumamente rápidas (`mongodb` en `1k`, `10k`, `50k` y `postgresql` en `1k`), `docker stats --no-stream` solo alcanzó a registrar **`2` muestras** (`samples_count = 2` en `results/summaries/`). Esto puede subestimar picos transitorios sub-segundo de RAM o CPU durante `load_ms` o `index_ms`.
4. **Timeout evaluado de forma pasiva post-retorno (`benchmark_runner.py:134-137`):** la comprobación de `BENCH_TIMEOUT_SECONDS = 60 s` compara el tiempo transcurrido después de que `execute_operation()` retorna; no aborta consultas colgadas en tiempo real (aunque en la campaña ninguna iteración superó los `81 ms` en operación individual).
5. **Deriva menor de entorno entre Fase 1 y Fase 2:** Docker Engine cambió de `29.7.2` a `29.9.3` y Python de `3.14.7` a `3.14.10` entre ambas fases (razón adicional por la cual no se comparan cifras absolutas entre Fase 1 y Fase 2).
6. **Contenedor único vs. despliegue integrado:** el benchmark levantó **un único motor a la vez** sobre Docker Desktop/WSL2 (Windows 11). No mide la contención de I/O, caché del sistema operativo y memoria cuando coexisten en paralelo **PostgreSQL (`768m`) + MongoDB (`768m`) + Neo4j (`1024m`) + FastAPI (`320m`) + Worker (`192m`)** dentro del presupuesto productivo de `3,072 MiB` (`4,096 MiB` techo).
7. **Inconsistencias documentales históricas detectadas en `biolink-benchmarking`:**
   - El reporte maestro `reports/20261121T050159Z_campaign_all_volumes_20261120.md` presenta pérdida de caracteres no ASCII (`?`) por codificación al exportarse en consola Windows.
   - Los archivos `README.md` y `docs/docs/benchmarking.md` seguían describiendo la campaña de 120 minutos como *"no ejecutada todavía"*, contradiciendo los 33 conjuntos de resultados reales ya presentes en `results/` y `reports/`.

---

## 6. Recomendaciones Técnicas Derivadas de las Limitaciones

1. **Medir almacenamiento físico real por volumen Docker** (`docker system df -v` o `du -sb`) tras ejecutar `ANALYZE` (PostgreSQL/MySQL), `compact`/`checkpoint` (MongoDB/CouchDB) e inspección de `/data/databases` en Neo4j, eliminando por completo el uso de `count(n)` y `memory_tracked` como sustitutos de disco.
2. **Validar empíricamente las mitigaciones implementadas en `biolink-backend`:** correr un experimento específico sobre `50,000` afirmaciones midiendo: (a) el impacto de `idx_assertion_published_r2_covering` sobre `R2_filtered_assertions` en PostgreSQL, y (b) el retiro por micro-lotes `IN TRANSACTIONS OF 1000 ROWS` junto con `NEO4J_TX_TOTAL_MAX=256m` en Neo4j sin disparar `MemoryPoolOutOfMemoryError`.
3. **Corregir la asimetría de Memgraph antes de comparaciones futuras de ingesta:** crear índices equivalentes sobre `:Taxon(taxon_id)`, `:InteractionAssertion(assertion_id)`, `:Evidence(evidence_id)` y `:Source(source_id)` en `prepare_schema()` antes de `load_dataset()`, evitando penalizar la carga con búsquedas sin índice.
4. **Evaluar escalamiento real de expedientes y concurrencia:** ampliar el límite de `taxa` y `taxon_dossiers` proporcionalmente al volumen `50,000` en futuras versiones del generador y agregar un escenario separado de carga concurrente multiusuario tanto directo como contra los endpoints `/api/v1` de `biolink-backend` (con el stack completo de 5 contenedores activos).
