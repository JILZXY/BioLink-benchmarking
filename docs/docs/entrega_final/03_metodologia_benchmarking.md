# Metodología Experimental del Benchmarking de BioLink (`03_metodologia_benchmarking.md`)

**Fecha de corte:** 21 de noviembre de 2026  
**Repositorio evaluado:** `biolink-benchmarking` (rama `development`, commit `1af5b77`)  
**Alcance documental:** Metodología, entorno, datos, cargas de trabajo, índices y métricas verificadas directamente en `src/biolink_bench/`, `docker/`, `datasets/`, `docs/` y los metadatos de ejecución de `results/summaries/`.

---

## 1. Objetivos del Benchmarking y Separación respecto a la API

El propósito de `biolink-benchmarking` es evaluar empíricamente **dos motores candidatos por cada paradigma de persistencia** requerido por BioLink (relacional, documental y orientado a grafos) antes de consolidar la selección tecnológica de `biolink-backend` (`README.md`, `docs/benchmark_protocol.md`, `docs/docs/benchmarking.md`).

### Objetivos específicos verificados en código y protocolo
1. **Medir el comportamiento directo de cada motor de base de datos** utilizando exclusivamente su controlador o protocolo nativo en Python (`psycopg`, `mysql-connector-python`, `pymongo`, cliente `httpx` sobre API HTTP nativa de CouchDB y `neo4j` vía Bolt), **sin intermediación de FastAPI, endpoints REST de `biolink-backend`, reglas HTTP de aplicación ni ORM como `SQLAlchemy`** (`docs/benchmark_protocol.md`, `docs/docs/benchmarking.md`).
2. **Validar corrección funcional exacta (`correctness_rate_pct`)** mediante oráculos deterministas en memoria sobre el conjunto de datos cargado (`workloads/*.py`): ningún motor puede declararse ganador por menor latencia si entrega resultados incorrectos o con fugas de registros no `PUBLISHED`.
3. **Evaluar estabilidad y huella de memoria bajo restricción estricta de recursos**, simulando el techo experimental global de **4,096 MiB (4 GiB)** fijado para la infraestructura del proyecto (`docs/resource_limits.md`, `config.py`).
4. **Caracterizar el escalamiento operativo** desde el *fixture* científico de referencia (`21` afirmaciones) hasta tres volúmenes sintéticos crecientes (`1,000`, `10,000` y `50,000` afirmaciones) dentro de una ventana máxima de campaña de **120 minutos**.

### Diferencia crítica entre benchmark directo y pruebas de carga de API
- **Benchmark directo (`biolink-benchmarking`):** mide conexión nativa, DDL/creación de esquema, carga inicial, construcción de índices, latencia de consulta/escritura por operación aislada y consumo del contenedor del motor.
- **Pruebas de API (`biolink-backend`):** miden el servicio FastAPI completo (enrutamiento HTTP, validación Pydantic v2, autenticación por cookie/Bearer, autorización RBAC, lógica de aplicación, orquestación multi-motor y respuestas JSON). Los tiempos aquí documentados pertenecen **exclusivamente** al benchmark directo.

### Orden de prioridad para la selección tecnológica (`docs/benchmark_protocol.md`, Sección 5)
1. Cumplimiento funcional y **100%** de corrección de resultados.
2. Integridad, trazabilidad y capacidad de reconstrucción.
3. Capacidad para completar los volúmenes objetivo (`1,000`; `10,000`; `50,000`).
4. Estabilidad y pico de memoria dentro del límite asignado por contenedor y del techo global de `4,096 MiB`.
5. Latencias (`p50`/`p95`), tiempo de carga y creación de índices.
6. Simplicidad operativa, calidad de controladores nativos y términos de licencia.

---

## 2. Motores Evaluados y 3. Versiones Utilizadas

Cada candidato fue ejecutado dentro de un contenedor Docker con etiqueta fija (prohibido `:latest` en `config.py:262`) y verificado por `RepoDigests` SHA-256 capturado en tiempo de ejecución (`results/summaries/*.json` y `docs/engine_matrix.md`).

| Paradigma | Candidato | Imagen Docker fijada | Versión exacta reportada por el servidor | Digest SHA-256 verificado (`RepoDigests`) | Driver / interfaz directa medida | Puerto `127.0.0.1` | Límite Docker | Licencia documentada (`03_matriz_comparativa_motores_biolink.csv`) |
|---|---|---|---|---|---|---:|---:|---|
| **Relacional** | MySQL 8.4 LTS | `mysql:8.4.13` | `8.4.13` (`MySQL Community Server - GPL`) | `mysql@sha256:a81d043930e51745522bd5c430961cf8286f0a23f0a9a2a6e0108f7ea71b0902` | `mysql-connector-python 26.10.0` | `3307` | `768 MiB` (`805,306,368 B`) | Community GPLv2 |
| **Relacional** | PostgreSQL 18.7 | `postgres:18.7` | `18.7 (Debian 18.7-1.pgdg13+5)` | `postgres@sha256:eb63372c1e05c755f55fa30cbd07aecc443676fc6c0fa90b9002d01537841e1a` | `psycopg 3.3.9` | `5433` | `768 MiB` (`805,306,368 B`) | Licencia PostgreSQL (permisiva) |
| **Documental** | MongoDB Community 8.0 | `mongo:8.0.38` | `8.0.38` | `mongo@sha256:479e85ced54ffb8a40dade1dcde2da2a9ae858515b9415e9cc54bfb8f0575d01` | `pymongo 4.20.1` | `27018` | `768 MiB` (`805,306,368 B`) | SSPL (*source-available*, no OSI) |
| **Documental** | Apache CouchDB 3.5.3 | `couchdb:3.5.3` | `3.5.3` | `couchdb@sha256:907eab5b7e55ab7cfd241d39b90b2a335ea40bef82acee5a37388c08bf201dda` | `httpx 0.28.1` (HTTP nativo de CouchDB) | `5985` | `768 MiB` (`805,306,368 B`) | Apache 2.0 |
| **Grafo** | Neo4j Community | `neo4j:2026.10.2-community` | `2026.10.2` (`community`) | `neo4j@sha256:88458a76de0704f543bab66b7df1984b36ac3f24de3c2e2d74c8fa1972ebb8cf` | `neo4j 6.4.1` (Bolt) | `7688` / `7475` | `1,024 MiB` (`1,073,741,824 B`) | GPLv3 Community |
| **Grafo** | Memgraph Community | `memgraph/memgraph:3.14.0` | `3.14.0` | `memgraph/memgraph@sha256:a732421217951066e42f5749111bc3d0c7b51b12c756be04850d4dafa84cc05e` | `neo4j 6.4.1` (cliente Bolt compatible) | `7689` | `1,024 MiB` (`1,073,741,824 B`) | Community (*in-memory*) |

### Desviaciones de versión y empaquetado documentadas (`docs/engine_matrix.md`)
1. **MySQL `8.4.12` → `mysql:8.4.13`:** la matriz previa de Etapa 3 (`docs/docs/03_matriz_comparativa_motores_biolink.csv`) citaba `8.4.12`, etiqueta inexistente en Docker Hub; se fijó `mysql:8.4.13`.
2. **Apache CouchDB `3.5.3` en Windows Docker Desktop:** montar `docker/document/couchdb/local.ini` con `:ro` provocaba error en `chmod -f 0644` durante `/docker-entrypoint.sh`; `docker/compose.yaml:118-123` genera `/opt/couchdb/etc/local.d/10-biolink.ini` dentro de la capa escribible del contenedor antes de arrancar. El uso de `httpx` responde a que HTTP/JSON es el protocolo nativo de CouchDB.
3. **PostgreSQL `18.7`:** el volumen `postgresql_bench_data` se monta en `/var/lib/postgresql` por compatibilidad con el esquema de directorio de PostgreSQL 18.

---

## 4. Entorno de Ejecución, Recursos Disponibles y Configuración Real

### 4.1 Hardware y software anfitrión observado (`results/summaries/*.json` → `host_info`)
Las 33 corridas en disco se agrupan en **dos fases cronológicas distintas** ejecutadas el `21 de noviembre de 2026` sobre el mismo sistema operativo (`Windows-11-10.0.26300-SP0`, arquitectura `AMD64`, WSL2 con `7.615 GiB` asignados a Docker según `docs/resource_limits.md:29`), con una actualización menor de Docker y Python entre ambas fases:

| Fase experimental | Ventana UTC (`2026-11-21`) | Corridas | Versión de Docker (`host_info.docker`) | Versión de Python (`host_info.python`) |
|---|---|---:|---|---|
| **Fase 1 (`smoke` + `scientific_fixture_v1`)** | `01:38:13Z` a `01:45:37Z` | `15` | `Docker version 29.7.2, build a7dcaa6` | `3.14.7` |
| **Fase 2 (Campaña sintética `10k`, `1k`, `50k`)** | `04:34:40Z` a `05:01:59Z` | `18` | `Docker version 29.9.3, build 5457199` | `3.14.10` |

### 4.2 Aislamiento de contenedores y parámetros aplicados por motor
Conforme a `docker/compose.yaml` y `runners/lifecycle.py` (`ensure_exclusive_engine`), **solo se levantó un contenedor de motor a la vez** sobre la red `biolink_bench_net`, asignando `2.0` CPU (`nano_cpus: 2000000000`) y volúmenes independientes eliminados con `docker compose ... down -v` al finalizar cada corrida comparativa (`run_pair_comparison` en `runners/benchmark_runner.py:211-222`).

| Motor | Límite Docker verificado (`docker_info`) | Parámetros efectivos verificados en ejecución (`compose.yaml` y `engine_info`) |
|---|---|---|
| `mysql` | `768.0 MiB` / `2.0` CPU | `docker/relational/mysql/my.cnf` declaraba `innodb_buffer_pool_size=256M`, `max_connections=50`, `performance_schema=OFF`; **sin embargo, en todas las corridas reportó `innodb_buffer_pool_size_bytes = 134,217,728` (`128 MiB`)** porque MySQL ignora archivos `.cnf` con permisos *world-writable* en montajes Windows (`docs/engine_matrix.md:38`). |
| `postgresql` | `768.0 MiB` / `2.0` CPU | Parámetros por CLI: `shared_buffers=192MB` (confirmado en `engine_info.shared_buffers`), `work_mem=8MB`, `maintenance_work_mem=64MB`, `effective_cache_size=384MB`, `max_connections=50`. |
| `mongodb` | `768.0 MiB` / `2.0` CPU | `--wiredTigerCacheSizeGB 0.25`. |
| `couchdb` | `768.0 MiB` / `2.0` CPU | `single_node = true`, `require_valid_user_except_for_up = true`. |
| `neo4j` | `1,024.0 MiB` / `2.0` CPU | `NEO4J_server_memory_heap_initial__size=256m`, `NEO4J_server_memory_heap_max__size=384m`, `NEO4J_server_memory_pagecache_size=256m`, `NEO4J_dbms_usage__report_enabled=false`. No fijó explícitamente `dbms.memory.transaction.total.max` (quedando en el tope interno reportado de `268.8 MiB`). |
| `memgraph` | `1,024.0 MiB` / `2.0` CPU | `--memory-limit=800` (MiB internos), `--log-level=WARNING`, `--also-log-to-stderr=true`. |

### 4.3 Convención estricta de unidades
- **Tiempo:** milisegundos (`ms`) medidos con `time.perf_counter_ns() / 1_000_000.0` (`benchmark_runner.py`). La duración global de campaña se expresa en minutos y segundos (`27 min 19 s`, límite `120 min`).
- **Memoria:** **MiB** ($1\text{ MiB} = 1{,}048{,}576\text{ bytes}$). `parse_memory_to_mib()` en `metrics/docker_monitor.py:11-28` normaliza las salidas de `docker stats` a **MiB** y `inspect_container()` divide `Memory / (1024 * 1024)`, aunque el campo JSON se llame `mem_limit_mb`. En Docker Compose (`768m`, `1024m`), `768m = 805,306,368 bytes = 768.0 MiB` y `1024m = 1,073,741,824 bytes = 1,024.0 MiB`.
- **CPU:** porcentaje reportado por `docker stats` sobre la cuota de `2.0` vCPU (por lo que valores entre `100%` y `200%` reflejan uso de más de un núcleo).

---

## 5. Volúmenes de Datos y Conjuntos Evaluados

Los conjuntos se definen en `src/biolink_bench/datasets/` y se verifican mediante hashes SHA-256 en sus manifiestos (`datasets/scientific_fixture/manifest.json` y `datasets/manifests/synthetic_*_manifest.json`).

| Entidad lógica | `scientific_fixture_v1` (Fase 1) | `synthetic_1000` (Fase 2, `1k`) | `synthetic_10000` (Fase 2, `10k`) | `synthetic_50000` (Fase 2, `50k`) | Motores que la reciben |
|---|---:|---:|---:|---:|---|
| `sources` | `2` | `7` | `40` | `40` | Relacional y Grafo |
| `source_versions` | `2` | `7` | `40` | `40` | Relacional |
| `localities` | `2` | `6` | `6` | `6` | Relacional y Grafo |
| `taxa` | `32` | `225` | `1,300` | `1,300` | Relacional y Grafo |
| `taxon_names` | `32` | `450` | `2,600` | `2,600` | Relacional |
| `taxon_identifiers` | `32` | `225` | `1,300` | `1,300` | Relacional |
| `interaction_types` | `3` | `3` | `3` | `3` | Relacional |
| `evidences` | `21` | `1,000` | `10,000` | `50,000` | Relacional (todas) / Grafo (solo vinculadas a `PUBLISHED`) |
| `assertions` (total) | `21` | `1,000` | `10,000` | `50,000` | Relacional |
| `published_assertions` | `21` (`100%`) | `838` (`83.8%`) | `8,475` (`84.8%`) | `42,523` (`85.0%`) | Relacional (`PUBLISHED`) y Grafo (proyección exclusiva) |
| `assertion_evidences` | `21` | `1,000` | `10,000` | `50,000` | Relacional / Grafo (`SUPPORTED_BY` solo `PUBLISHED`) |
| `import_batches` | `1` | `10` | `10` | `10` | Relacional |
| `import_records` | `21` | `1,000` | `10,000` | `50,000` | Relacional |
| `review_events` | `21` | `893` | `8,997` | `45,071` | Relacional |
| `taxon_dossiers` | `32` | `225` | `1,300` | `1,300` | Documental |
| `study_dossiers` | `2` | `7` | `40` | `40` | Documental |
| `raw_source_records` | `21` | `1,000` | `10,000` | `50,000` | Documental |
| **Tamaño JSON/JSONL en origen** | `24,158 B` | `3,048,529 B` (`2.91 MiB`) | `28,238,364 B` (`26.93 MiB`) | `129,224,011 B` (`123.24 MiB`) | Fuente lógica de carga |
| **SHA-256 manifiesto** | `f4b2ec40...94bed73` | `a35e0114...1bc321c0` | `0e2e17c2...4247c86` | `00fef827...554b9b6eb` | Trazabilidad |

> **Observación estructural del generador sintético (`synthetic_generator.py:68-70`):** el algoritmo limita deliberadamente `num_animals = max(10, min(500, N // 10))`, `num_plants = max(15, min(800, N // 8))` y `num_sources = max(4, min(40, N // 250 + 3))`. Por ello, **entre `10,000` y `50,000` afirmaciones**, las entidades `taxa` (`1,300`), `taxon_names` (`2,600`), `taxon_dossiers` (`1,300`), `sources` (`40`) y `study_dossiers` (`40`) **mantienen exactamente la misma cardinalidad**, escalando únicamente `assertions`, `evidences`, `import_records`, `review_events` y `raw_source_records`.

---

## 6. Procedimiento de Carga y Fases de Ejecución

El controlador `run_engine_benchmark()` (`src/biolink_bench/runners/benchmark_runner.py:42-194`) separa estrictamente preparación, carga, indexación, calentamiento y medición:

1. **Validación previa e inicio aislado (`validate_config`, `compose_up_engine`):** verifica etiquetas sin `:latest`, puertos locales y exclusividad de contenedor. Inicia `DockerResourceMonitor` con intervalo de muestreo de `0.5 s` (`BENCH_STATS_INTERVAL_SECONDS=0.5`).
2. **Conexión (`connection_ms`):** abre conexión/sesión nativa y registra `engine_info`.
3. **Preparación de esquema (`schema_ms`):**
   - `mysql` / `postgresql`: crea **15 tablas** (`app_user`..`outbox_event`) e inserta 3 usuarios de prueba (`BENCH_USERS`).
   - `mongodb`: crea 4 colecciones e instala validador `$jsonSchema` en `taxon_dossiers`.
   - `couchdb`: crea 4 bases de datos (`biolink_bench_*`) e instala `_design/biolink_validation` (`validate_doc_update`).
   - `neo4j` / `memgraph`: aplica **5 restricciones `UNIQUE`** sobre IDs de nodos (`Taxon`, `InteractionAssertion`, `Locality`, `Evidence`, `Source`).
4. **Carga inicial (`load_ms`):** limpia registros previos con ese `dataset_tag` e inserta en lotes:
   - `mysql` / `postgresql` (`_common.py`): lotes de **500 filas** vía `executemany` en orden topológico de claves foráneas dentro de **una sola transacción** (`mysql` hace un `commit()` final; `postgresql` usa `with conn.transaction():`).
   - `mongodb` (`mongodb_adapter.py:102-106`): `insert_many(..., ordered=True)` en lotes de **1,000 documentos**.
   - `couchdb` (`couchdb_adapter.py:92-100`): `POST /{db}/_bulk_docs` en lotes de **500 documentos**.
   - `neo4j` / `memgraph` (`neo4j_adapter.py:86-176`, `memgraph_adapter.py:93-183`): inserción por lotes de **500 elementos** con `UNWIND $rows AS r MERGE ...` proyectando únicamente `published_assertions` y sus evidencias/fuentes.
5. **Creación de índices secundarios (`index_ms`):** se ejecuta **después** de `load_dataset` y **antes** de las consultas, midiendo por separado el costo de construcción de índices.
6. **Calentamiento y medición (`warmup_ms`, `measure`):**
   - En Fase 1 (`fixture`): `warmup = 0`, `iterations = 1` por workload (`4` filas CSV por corrida).
   - En Fase 2 (`1k`, `10k`, `50k`): `warmup = 5`, `iterations = 30` por cada uno de los `4` workloads del modelo (`4 × 35 = 140` filas CSV por corrida: `20` de calentamiento + `120` medidas). Las lecturas siempre preceden a las escrituras (`R1→R2→R3→R4`, `D1→D2→D3→D4`, `G1→G2→G3→G4`) para preservar el conjunto base contra el cual se validan las consultas de lectura.
7. **Almacenamiento, limpieza (`cleanup_ms`) y apagado:** consulta `get_storage_bytes()`, elimina todos los registros sintéticos (`DELETE` en cascada ordenada en SQL, `delete_many` en MongoDB, `_find` + `_bulk_docs` con `_deleted: true` de `500` en CouchDB, `MATCH (n {dataset_tag}) WITH n LIMIT 2000 DETACH DELETE n` en grafos), detiene el monitor Docker, cierra volumen (`down -v`) y exporta CSV, JSON, LOG y reporte Markdown.

---

## 7. Esquemas, Restricciones e Índices Utilizados por Candidato

| Paradigma | Motor | Restricciones estructurales en `prepare_schema()` | Índices secundarios creados en `create_indexes()` | Particularidades relevantes |
|---|---|---|---|---|
| **Relacional** | MySQL `8.4.13` (`mysql_adapter.py`) | `PRIMARY KEY` en 14 tablas + PK compuesta en `assertion_evidence`, `UNIQUE (scheme, external_id)` y `UNIQUE (code)`, FKs InnoDB | `idx_taxon_name_lookup (name, taxon_id)`, `idx_taxon_accepted (accepted_name)`, `idx_assertion_filter (status, locality_id, period_start, period_end)`, `idx_assertion_actor (actor_taxon_id)`, `idx_assertion_target (target_taxon_id)`, `idx_import_record_batch (import_batch_id)` | InnoDB agrupa (*clustered index*) por `PRIMARY KEY` e **indexa automáticamente las columnas FK** (`import_record`, `review_event`, `assertion_evidence`, etc.). `outbox_event.payload_json` usa tipo `JSON`. |
| **Relacional** | PostgreSQL `18.7` (`postgresql_adapter.py`) | Mismas PK, `UNIQUE` y FKs declaradas en SQL | Exactamente los mismos **6 índices** `B-Tree` que MySQL sobre los mismos prefijos de columna. | PostgreSQL **no crea índices automáticos en columnas FK** ni incluye `assertion_id` en `idx_assertion_filter`. `outbox_event.payload_json` usa `JSONB`. No se ejecutó `ANALYZE` tras `load_dataset` y tampoco incluye el índice cubriente posterior `idx_assertion_published_r2_covering` del backend. |
| **Documental** | MongoDB `8.0.38` (`mongodb_adapter.py`) | Validador `$jsonSchema` en `taxon_dossiers` + índice único implícito `_id` en las 4 colecciones | `idx_taxon_id`, **`idx_claims_nested (dataset_tag, claims.field, claims.value)`** (índice multikey compuesto), `idx_tag_group`, `idx_version_history`, `idx_raw_batch` | Indexa directamente elementos internos del arreglo `claims`, acelerando consultas `$elemMatch` (`D2`). |
| **Documental** | CouchDB `3.5.3` (`couchdb_adapter.py`) | `_design/biolink_validation` (`validate_doc_update` en JS exigiendo `document_type`, `schema_version`, `dataset_tag`) + índice primario `_id` | 4 índices Mango JSON: `idx_taxon_id ([taxon_id])`, `idx_tag_group ([dataset_tag, organism_group])`, `idx_version_history`, `idx_raw_batch` | **No define índice Mango equivalente para `claims` (`$elemMatch`)** porque la indexación de subcampos dentro de arreglos en Mango difiere en soporte/diseño, forzando escaneo tras filtrado en `D2`. |
| **Grafo** | Neo4j `2026.10.2` (`neo4j_adapter.py`) | 5 `CREATE CONSTRAINT ... IS UNIQUE` (`Taxon.taxon_id`, `InteractionAssertion.assertion_id`, `Locality.locality_id`, `Evidence.evidence_id`, `Source.source_id`) | 3 índices secundarios: `Taxon(organism_group)`, **`InteractionAssertion(status, interaction_type_code, period_start)`** (compuesto), `Locality(spatial_validation_status)` | En Neo4j, toda restricción `UNIQUE` crea automáticamente un índice de respaldo **desde `prepare_schema()`**, acelerando los `MATCH`/`MERGE` durante `load_dataset`. |
| **Grafo** | Memgraph `3.14.0` (`memgraph_adapter.py`) | 5 `CREATE CONSTRAINT ON (...) ASSERT ... IS UNIQUE;` sobre las mismas 5 etiquetas | 5 índices simples creados **después** de la carga: `:Taxon(taxon_id)`, `:Taxon(organism_group)`, `:InteractionAssertion(assertion_id)`, `:InteractionAssertion(status)`, `:Locality(locality_id)` | En Memgraph, **una restricción `UNIQUE` no crea automáticamente un *label-property index* de búsqueda** (`CREATE INDEX` corre después en `create_indexes()`); además faltan índices en `Evidence(evidence_id)`, `Source(source_id)`, `interaction_type_code` y `period_start`. |

---

## 8. Consultas y Escenarios Evaluados (`workloads/*.py` y `docs/workloads.md`)

| Paradigma | ID | Operaciones BioLink origen | Tipo | Descripción funcional y mecanismo de validación en memoria |
|---|---|---|---|---|
| **Relacional** | `R1_taxon_search` | `OP-01` | Lectura | `JOIN taxon_name`–`taxon` filtrando por `tn.name = %s` exacto (alternando nombres aceptados y sinónimos del bundle). Valida conjunto exacto de `taxon_id`. |
| **Relacional** | `R2_filtered_assertions` | `OP-03`, `OP-05` | Lectura | Filtra `interaction_assertion JOIN interaction_type` por `locality_id`, `period_start >= %s` y `status = 'PUBLISHED'`, ordenando por `assertion_id LIMIT 50`. Valida orden exacto y cero no publicados. |
| **Relacional** | `R3_transactional_assertion_outbox` | `OP-11`, `OP-12` | Escritura ACID | Una sola transacción que inserta `evidence`, `interaction_assertion` (`PUBLISHED`), `assertion_evidence`, `review_event` y `outbox_event` (`PENDING`). Valida `committed=True` e IDs retornados. |
| **Relacional** | `R4_batch_import_insert` | `OP-09`, `OP-10` | Escritura lote | Transacción que inserta `1` `import_batch` y `50` `import_record` mediante `executemany`. Valida `inserted_records == 50` y `import_batch_id`. |
| **Documental** | `D1_read_taxon_dossier` | `OP-02` | Lectura puntual | Recupera `taxon_dossier` por `_id`/`taxon_id` (`find_one` en MongoDB; `GET /{db}/{id}` en CouchDB). Valida `taxon_id` y conteo mínimo de `claims`. |
| **Documental** | `D2_nested_attribute_query` | `OP-02`, `OP-13` | Lectura anidada | Consulta por `dataset_tag` y `$elemMatch` en `claims` (`field = 'ecology.diet'`, alternando entre 3 valores: `SYN_DIET_FRUGIVORE`, `SYN_DIET_MIXED_FRUIT`, `SYN_PRODUCER`), ordenado por `taxon_id LIMIT 50`. Valida lista ordenada exacta. |
| **Documental** | `D3_versioned_dossier_update` | `OP-13` | Escritura versionada | Lee documento vigente, archiva snapshot en `taxon_dossier_versions` (`{tid}::v{old}::{seq}`) y actualiza `document_version + 1` agregando un `claim` (respetando `_rev` en CouchDB). Valida `new_version == previous_version + 1`. |
| **Documental** | `D4_bulk_raw_source_insert` | `OP-09`, `OP-10` | Escritura masiva | Inserta lote de `50` documentos `raw_source_record` (`insert_many` en MongoDB; `POST /_bulk_docs` en CouchDB). Valida `inserted_count == 50`. |
| **Grafo** | `G1_taxon_neighbors` | `OP-03` | Lectura vecindario | Patrón `(actor:Taxon)-[:ACTOR_IN]->(a:InteractionAssertion)-[:TARGETS]->(target:Taxon)` + `(a)-[:OBSERVED_AT]->(l:Locality)` con `WHERE a.status='PUBLISHED' AND (actor.taxon_id=$id OR target.taxon_id=$id)` ordenado por `a.assertion_id`. Valida conjunto `(assertion_id, partner_taxon_id)`. |
| **Grafo** | `G2_filtered_subgraph` | `OP-05` | Lectura subgrafo | Filtra afirmaciones `PUBLISHED` por `l.locality_id`, `a.interaction_type_code` y `a.period_start >= $period_start`, `ORDER BY a.assertion_id LIMIT 100`. Valida lista exacta y ausencia de mezcla espacial. |
| **Grafo** | `G3_distinct_partner_count` | `OP-07` | Lectura analítica | Calcula por separado `count(DISTINCT partner_id)` y `count(DISTINCT assertion_id)` en vecinos `PUBLISHED` del taxón. Valida ambos conteos exactos. |
| **Grafo** | `G4_idempotent_assertion_upsert` | `OP-12` | Escritura idempotente | `MATCH` de `actor`, `target` y `loc`, seguido de `MERGE` sobre `Source`, `Evidence`, `InteractionAssertion` y 4 aristas; la mitad de iteraciones (`i // 2`) reutiliza el mismo `assertion_id` para comprobar idempotencia real sin duplicar nodos ni aristas. |

---

## 9. Métricas Recolectadas y Criterios de Comparabilidad

### 9.1 Estadísticos calculados (`src/biolink_bench/metrics/collector.py`)
- **Exclusión del calentamiento:** solo registros con `is_warmup == False` y `ok == True` entran en percentiles, promedios y throughput (`n = 30` por operación en Fase 2).
- **Percentiles (`p50_ms`, `p95_ms`):** interpolación lineal sobre el rango `(N - 1) * (pct / 100.0)` de las latencias ordenadas.
- **Throughput secuencial (`ops_per_sec`):** `ok_count / (sum(ok_latencies) / 1000.0)` con cliente monohilo secuencial (`concurrency = 1`).
- **Corrección (`correctness_rate_pct`):** `(valid_count / total) * 100.0`.
- **Recursos Docker (`metrics/docker_monitor.py`):** hilo en segundo plano cada `0.5 s` ejecutando `docker stats --no-stream` para capturar `peak_memory_mib`, `avg_memory_mib`, `peak_cpu_pct`, `avg_cpu_pct` y `samples_count`, más `docker inspect` posterior para verificar `oom_killed`.

### 9.2 Qué mide realmente `storage_bytes` en cada motor (advertencia crítica de comparabilidad)

| Motor | Implementación en `get_storage_bytes()` | Naturaleza real de la cifra | ¿Comparable en bytes físicos en disco? |
|---|---|---|---|
| `mysql` | `SELECT SUM(data_length + index_length) FROM information_schema.TABLES` (`mysql_adapter.py:669`) | Estimación cacheada del motor InnoDB sin `ANALYZE TABLE` previo (puede subestimar o desfasarse entre volúmenes). | Parcial (aproximada, sensible a caché de estadísticas). |
| `postgresql` | `SELECT pg_database_size(current_database())` (`postgresql_adapter.py:604`) | Tamaño real en disco del directorio completo de la base de datos (incluye ~`8.54 MB` de catálogo base + tablas e índices). | Sí en disco interno PG, no equivalente neto al modelo documental/grafo. |
| `mongodb` | `db.command("dbStats")` → `storageSize + indexSize` (`mongodb_adapter.py:218`) | Espacio asignado comprimido por WiredTiger en colecciones e índices (antes de checkpoints diferidos en corridas cortas). | Solo aproximada dentro de MongoDB. |
| `couchdb` | Suma de `sizes.active` (o `file`) sobre las 4 bases (`couchdb_adapter.py:247`) | Bytes activos lógicos de árboles B+ de documentos sin contar sobrecarga total de compactación/vistas. | Parcial dentro de CouchDB. |
| `neo4j` | `MATCH (n) RETURN count(n) AS nodes` (`neo4j_adapter.py:334`) | **PROXY: conteo total de nodos** (carece de procedimiento Cypher estándar en Community para consultar bytes en disco). | **NO — Nunca debe interpretarse como bytes reales en disco.** |
| `memgraph` | `SHOW STORAGE INFO;` → `memory_tracked` (`memgraph_adapter.py:349`) | **Bytes en memoria RAM rastreados internamente por Memgraph** (motor *in-memory*), no tamaño físico en disco. | **NO — Representa RAM asignada internamente, no disco.** |
