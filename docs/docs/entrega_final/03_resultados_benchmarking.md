# Resultados del Benchmarking y Justificación de la Selección Tecnológica (`03_resultados_benchmarking.md`)

**Fecha de corte:** 21 de noviembre de 2026  
**Fuentes originales verificadas:** `biolink-benchmarking/results/raw/*.csv` (`33` archivos), `results/summaries/*.json` (`33` archivos), `results/logs/*.log` (`33` archivos) y `reports/*.md` (`44` archivos, incluidos los `9` reportes comparativos y el consolidado maestro `20261121T050159Z_campaign_all_volumes_20261120.md`).  
**Integridad verificada:** La verificación cruzada directa entre los CSV brutos y los resúmenes JSON arrojó **0 discrepancias** de cálculo en las `33` corridas en disco.

---

## 1. Inventario Cronológico de Corridas y Reglas de Comparación Aplicadas

Las mediciones originales se agrupan en **dos fases experimentales separadas**, que se documentan en tablas independientes para no mezclar entornos ni tamaños muestrales:

1. **Fase 1 — Validación técnica `smoke` (`8` corridas) y *fixture* científico `scientific_fixture_v1` (`7` corridas):** ejecutada el `2026-11-21` entre `01:38:13Z` y `01:45:37Z` (`Docker 29.7.2`, `Python 3.14.7`, `warmup=0`, `iterations=1`). Incluyó la falla inicial `20261121T014334Z_smoke_memgraph_3b7eb4` y su repetición tras corrección (`014458Z`), así como dos validaciones sucesivas de Neo4j (`27953d`/`59c675` y `7d69e5`/`8f5203`).
2. **Fase 2 — Campaña sintética multi-volumen (`18` corridas):** ejecutada secuencialmente el `2026-11-21` entre `04:34:40Z` y `05:01:59Z` (**27 min 19 s** totales frente al límite de `120 min`), sobre `Docker 29.9.3` y `Python 3.14.10`, siguiendo el orden cronológico **`10,000` → `1,000` → `50,000`** afirmaciones con semilla única `20261120`, `5` iteraciones de calentamiento y `30` medidas por operación (`140` filas CSV por corrida; `2,520` mediciones totales registradas en Fase 2).

En las **18 corridas de Fase 2**, las `2,160` mediciones oficiales (`18 × 120`) obtuvieron **100.00% de corrección** y **0 timeouts** (`OOMKilled = False` en todos los contenedores). Sin embargo, **Neo4j a `50,000` falló durante la fase de limpieza posterior** (`cleanup_test_data`) por `MemoryPoolOutOfMemoryError`.

---

## 2. Resultados de Fase 1: Conectividad `smoke` y *Fixture* Científico (`21` afirmaciones)

> **Advertencia metodológica:** Con `warmup=0` e `iterations=1`, los tiempos de Fase 1 están dominados por compilación de planes en frío/JIT (JVM en Neo4j) y caché inicial. Solo respaldan **conectividad directa, salud y 100% de corrección funcional**, nunca comparación estadística de latencia frente a Fase 2.

### 2.1 Validación `smoke` (`SMOKE_CRUD`)

| Corrida (`run_id`) | Motor (`versión`) | Conexión (ms) | `SMOKE_CRUD` (ms) | Pico RAM (MiB) | `OOM` | Errores registrados |
|---|---|---:|---:|---:|---|---|
| `20261121T013813Z_smoke_mysql_94cf9b` | `mysql` (`8.4.13`) | `52.44` | `1,190.27` | `445.90` | `False` | `0` |
| `20261121T013844Z_smoke_postgresql_9c6e22` | `postgresql` (`18.7`) | `23.21` | `54.00` | `57.98` | `False` | `0` |
| `20261121T013956Z_smoke_mongodb_5d4593` | `mongodb` (`8.0.38`) | `319.28` | `134.89` | `299.00` | `False` | `0` |
| `20261121T014159Z_smoke_couchdb_f143cd` | `couchdb` (`3.5.3`) | `232.77` | `445.83` | `154.10` | `False` | `0` |
| `20261121T014257Z_smoke_neo4j_27953d` | `neo4j` (`2026.10.2`) | `139.90` | `1,764.09` | `661.80` | `False` | `0` |
| `20261121T014334Z_smoke_memgraph_3b7eb4` | `memgraph` (`3.14.0`) | `3.28` | `36.49` | `62.21` | `False` | **`KeyError: 'name'`** en `get_storage_bytes()` (`storage_bytes=None`, versión `unknown`) |
| `20261121T014458Z_smoke_memgraph_dae560` | `memgraph` (`3.14.0`) | `3.33` | `40.85` | `62.96` | `False` | `0` (corrida repetida tras corregir columna `'storage info'`) |
| `20261121T014525Z_smoke_neo4j_7d69e5` | `neo4j` (`2026.10.2`) | `124.67` | `1,896.20` | `663.60` | `False` | `0` |

### 2.2 Comprobación en *fixture* científico (`scientific_fixture_v1`, `n=1`, `warmup=0`)

| Corrida (`run_id`) | Motor | Carga (ms) | Índices (ms) | Limpieza (ms) | Pico RAM (MiB) | Latencias de iteración única (`Op1 / Op2 / Op3 / Op4` en ms) | Corrección |
|---|---|---:|---:|---:|---:|---|---:|
| `20261121T013817Z_bench_mysql_3609b6` | `mysql` | `40.49` | `320.43` | `27.31` | `451.20` | `R1: 2.46` / `R2: 2.84` / `R3: 19.14` / `R4: 17.00` | `100%` |
| `20261121T013849Z_bench_postgresql_6c9e17` | `postgresql` | `30.17` | `5.57` | `11.50` | `58.94` | `R1: 0.96` / `R2: 1.46` / `R3: 4.63` / `R4: 3.33` | `100%` |
| `20261121T014001Z_bench_mongodb_233882` | `mongodb` | `8.68` | `426.26` | `3.92` | `206.50` | `D1: 1.15` / `D2: 2.18` / `D3: 2.98` / `D4: 1.65` | `100%` |
| `20261121T014204Z_bench_couchdb_e74d82` | `couchdb` | `142.84` | `70.88` | `159.50` | `163.90` | `D1: 2.69` / `D2: 5.57` / `D3: 47.66` / `D4: 21.20` | `100%` |
| `20261121T014306Z_bench_neo4j_59c675` | `neo4j` | `789.72` | `101.34` | `75.29` | `710.40` | `G1: 471.15` / `G2: 246.92` / `G3: 176.44` / `G4: 213.14` | `100%` |
| `20261121T014502Z_bench_memgraph_b46fc2` | `memgraph` | `33.58` | `5.84` | `3.01` | `72.10` | `G1: 2.01` / `G2: 2.77` / `G3: 4.23` / `G4: 89.96` | `100%` |
| `20261121T014531Z_bench_neo4j_8f5203` | `neo4j` | `930.73` | `137.04` | `56.43` | `700.00` | `G1: 435.19` / `G2: 197.50` / `G3: 174.31` / `G4: 198.32` | `100%` |

---

## 3. Experimentos Relacionales (`MySQL 8.4.13` vs. `PostgreSQL 18.7`) — Fase 2

**Respaldo documental original:**  
- `1,000`: `results/summaries/20261121T043920Z_bench_mysql_57c194.json`, `20261121T043939Z_bench_postgresql_6f16bc.json`, `reports/20261121T043949Z_compare_relational_0cfd2f.md`.  
- `10,000`: `results/summaries/20261121T043440Z_bench_mysql_1693e5.json`, `20261121T043459Z_bench_postgresql_4cb5de.json`, `reports/20261121T043515Z_compare_relational_2b1f46.md`.  
- `50,000`: `results/summaries/20261121T044136Z_bench_mysql_a62a14.json`, `20261121T044206Z_bench_postgresql_530dc1.json`, `reports/20261121T044353Z_compare_relational_c101be.md`.

### 3.1 Fases de ciclo de vida, memoria, CPU y almacenamiento reportado (límite `768.0 MiB`)

| Volumen | Motor | Conexión (ms) | Esquema (ms) | Carga (ms) | Índices (ms) | Limpieza (ms) | Pico RAM (MiB) | Prom. RAM (MiB) | Pico CPU (%) | `OOM` | Almacenamiento reportado (bytes) y nota |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `1,000` | `mysql` | `55.41` | `490.24` | `815.28` | `241.94` | `127.68` | `503.60` | `500.63` | `25.31` | `False` | `2,031,616` *(est. `information_schema`)* |
| `1,000` | `postgresql` | `33.79` | `30.96` | `157.20` | `10.50` | `92.72` | `73.92` | `73.92` | `31.83` | `False` | `10,991,295` *(`pg_database_size`, incl. catálogo)* |
| `10,000` | `mysql` | `16.55` | `49.55` | `2,850.00` | `615.95` | `1,022.65` | `547.60` | `504.62` | `83.07` | `False` | `1,736,704` *(est. InnoDB sin `ANALYZE`)* |
| `10,000` | `postgresql` | `8.74` | `24.76` | `1,366.70` | `62.30` | `3,906.95` | `91.70` | `87.09` | `103.84` | `False` | `23,049,919` *(`pg_database_size`)* |
| `50,000` | `mysql` | `19.40` | `555.54` | `8,744.70` | `727.67` | `3,974.51` | `614.80` | `532.90` | `111.73` | `False` | `57,638,912` *(est. `information_schema`)* |
| `50,000` | `postgresql` | `31.93` | `24.29` | `6,484.71` | `180.87` | **`88,953.18`** | **`124.80`** | `117.63` | `106.19` | `False` | `70,915,775` *(`pg_database_size`)* |

### 3.2 Latencias por operación (`warmup = 5`, `n = 30`, `100.00%` corrección, `0` errores/timeouts)

| Volumen | Operación | Motor | `min` (ms) | `p50` (ms) | `mean` (ms) | `p95` (ms) | `max` (ms) | `ops/s` (monohilo) |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| `1,000` | `R1_taxon_search` | `mysql` | `1.353` | `2.260` | `2.354` | `4.218` | `5.949` | `424.84` |
| `1,000` | `R1_taxon_search` | `postgresql` | `0.346` | **`0.453`** | `0.487` | **`0.673`** | `1.111` | **`2,051.82`** |
| `1,000` | `R2_filtered_assertions` | `mysql` | `1.942` | `2.488` | `2.789` | `3.971` | `4.269` | `358.57` |
| `1,000` | `R2_filtered_assertions` | `postgresql` | `0.465` | **`0.774`** | `0.785` | **`1.174`** | `1.290` | **`1,274.35`** |
| `1,000` | `R3_transactional_assertion_outbox` | `mysql` | `5.839` | `7.297` | `10.149` | `21.669` | `23.026` | `98.54` |
| `1,000` | `R3_transactional_assertion_outbox` | `postgresql` | `2.605` | **`2.970`** | `3.193` | **`4.415`** | `5.217` | **`313.16`** |
| `1,000` | `R4_batch_import_insert` | `mysql` | `7.143` | `9.965` | `13.090` | `25.497` | `27.426` | `76.39` |
| `1,000` | `R4_batch_import_insert` | `postgresql` | `2.741` | **`3.563`** | `3.462` | **`4.011`** | `4.205` | **`288.82`** |
| `10,000` | `R1_taxon_search` | `mysql` | `1.096` | `1.435` | `1.470` | `1.952` | `2.021` | `680.22` |
| `10,000` | `R1_taxon_search` | `postgresql` | `0.409` | **`0.501`** | `0.530` | **`0.660`** | `1.042` | **`1,887.94`** |
| `10,000` | `R2_filtered_assertions` | `mysql` | `1.448` | **`1.659`** | `1.753` | **`2.222`** | `3.021` | **`570.33`** |
| `10,000` | `R2_filtered_assertions` | `postgresql` | `1.049` | `1.886` | `1.957` | `2.582` | `6.162` | `511.09` |
| `10,000` | `R3_transactional_assertion_outbox` | `mysql` | `5.757` | `6.799` | `9.209` | `20.302` | `20.693` | `108.59` |
| `10,000` | `R3_transactional_assertion_outbox` | `postgresql` | `2.473` | **`2.820`** | `3.004` | **`3.877`** | `5.002` | **`332.88`** |
| `10,000` | `R4_batch_import_insert` | `mysql` | `5.080` | `6.022` | `8.639` | `20.116` | `20.820` | `115.76` |
| `10,000` | `R4_batch_import_insert` | `postgresql` | `2.945` | **`3.322`** | `3.407` | **`3.954`** | `4.305` | **`293.52`** |
| `50,000` | `R1_taxon_search` | `mysql` | `1.104` | `1.255` | `1.292` | `1.549` | `1.654` | `774.01` |
| `50,000` | `R1_taxon_search` | `postgresql` | `0.459` | **`0.520`** | `0.559` | **`0.694`** | `1.014` | **`1,790.56`** |
| `50,000` | `R2_filtered_assertions` | `mysql` | `1.410` | **`1.746`** | `2.075` | **`3.600`** | `4.123` | **`481.82`** |
| `50,000` | `R2_filtered_assertions` | `postgresql` | `2.759` | **`6.727`** | `6.333` | **`9.403`** | `9.880` | `157.90` |
| `50,000` | `R3_transactional_assertion_outbox` | `mysql` | `4.648` | `5.280` | `5.536` | `7.954` | `9.484` | `180.64` |
| `50,000` | `R3_transactional_assertion_outbox` | `postgresql` | `2.473` | **`2.797`** | `2.936` | **`3.868`** | `4.568` | **`340.64`** |
| `50,000` | `R4_batch_import_insert` | `mysql` | `4.341` | `4.935` | `5.052` | `5.925` | `6.746` | `197.95` |
| `50,000` | `R4_batch_import_insert` | `postgresql` | `2.533` | **`3.185`** | `3.251` | **`3.805`** | `5.855` | **`307.60`** |

### 3.3 Análisis comparativo relacional
- **Dónde dominó PostgreSQL `18.7`:** consumió **4.9× menos RAM pico** en `50k` (`124.80 MiB` = `16.3%` de `768 MiB`, frente a `614.80 MiB` = `80.1%` en MySQL), cargó `50k` filas en `6,484.71 ms` (`25.8%` más rápido que MySQL), construyó los `6` índices en `180.87 ms` (`4.0×` más rápido) y mantuvo amplia ventaja estable en búsqueda taxonómica (`R1`: `0.520 ms` vs `1.255 ms`), inserción transaccional Outbox (`R3`: `2.797 ms` vs `5.280 ms`, soportado por `JSONB` nativo) y lotes (`R4`: `3.185 ms` vs `4.935 ms`).
- **Hallazgos desfavorables a PostgreSQL que no deben omitirse:**
  1. **Degradación de `R2_filtered_assertions` con el crecimiento:** pasó de `0.774 ms` (`1k`) a `1.886 ms` (`10k`) y **`6.727 ms` (`p95 = 9.403 ms`) en `50k`**, quedando **3.85× más lento** que MySQL (`1.746 ms`). Esto se explica porque el índice de prueba `idx_assertion_filter (status, locality_id, period_start, period_end)` no incluía `assertion_id` ni columnas cubrientes, y el adaptador tampoco ejecutó `ANALYZE` tras la carga masiva. Este resultado negativo motivó el diseño de `idx_assertion_published_r2_covering` (`INCLUDE (...) WHERE status = 'PUBLISHED'`) en `biolink-backend/database/postgresql/migrations/002_create_indexes.sql`.
  2. **Limpieza masiva muy lenta (`cleanup_ms = 88,953.18 ms` en `50k`, frente a `3,974.51 ms` en MySQL):** los `DELETE` encadenados sobre tablas hijas (`outbox_event`, `review_event`, `assertion_evidence`, `import_record`) carecían de índices en las columnas FK de PostgreSQL, mientras MySQL InnoDB indexa FKs automáticamente (`postgresql_adapter.py:219-226`, `546-578`).

---

## 4. Experimentos Documentales (`MongoDB 8.0.38` vs. `Apache CouchDB 3.5.3`) — Fase 2

**Respaldo documental original:**  
- `1,000`: `results/summaries/20261121T044019Z_bench_mongodb_e8e5d5.json`, `20261121T044029Z_bench_couchdb_00d5d2.json`, `reports/20261121T044042Z_compare_document_d98c9a.md`.  
- `10,000`: `results/summaries/20261121T043515Z_bench_mongodb_b65cb2.json`, `20261121T043525Z_bench_couchdb_483b5f.json`, `reports/20261121T043542Z_compare_document_1a32e9.md`.  
- `50,000`: `results/summaries/20261121T044402Z_bench_mongodb_cddcb0.json`, `20261121T044412Z_bench_couchdb_c198d9.json`, `reports/20261121T044438Z_compare_document_847363.md`.

### 4.1 Fases de ciclo de vida, memoria, CPU y almacenamiento reportado (límite `768.0 MiB`)

| Volumen | Motor | Conexión (ms) | Esquema (ms) | Carga (ms) | Índices (ms) | Limpieza (ms) | Pico RAM (MiB) | Prom. RAM (MiB) | Pico CPU (%) | `OOM` | Almacenamiento reportado (bytes) y nota |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `1,000` | `mongodb` | `27.52` | `38.00` | `23.90` | `41.83` | `16.20` | `407.00` | `406.95` | `9.94` | `False` | `122,880` *(`dbStats storage+index`)* |
| `1,000` | `couchdb` | `127.26` | `65.46` | `339.51` | `26.23` | `552.18` | `169.40` | `165.73` | `133.78` | `False` | `2,067,380` *(`sizes.active`)* |
| `10,000` | `mongodb` | `29.41` | `62.94` | `186.34` | `162.66` | `61.72` | `418.20` | `418.05` | `19.79` | `False` | `229,376` *(`dbStats`, pre-checkpoint)* |
| `10,000` | `couchdb` | `113.14` | `62.07` | `1,596.89` | `25.72` | `2,494.83` | `184.20` | `174.68` | `170.59` | `False` | `9,976,076` *(`sizes.active`)* |
| `50,000` | `mongodb` | `13.20` | `35.88` | **`773.56`** | `102.92` | `232.25` | `269.90` | `264.25` | `29.47` | `False` | `8,060,928` *(`dbStats`)* |
| `50,000` | `couchdb` | `110.98` | `70.34` | `5,015.91` | `40.78` | `8,635.60` | **`212.80`** | `187.10` | `196.53` | `False` | `40,487,769` *(`sizes.active`)* |

### 4.2 Latencias por operación (`warmup = 5`, `n = 30`, `100.00%` corrección, `0` errores/timeouts)

| Volumen | Operación | Motor | `min` (ms) | `p50` (ms) | `mean` (ms) | `p95` (ms) | `max` (ms) | `ops/s` (monohilo) |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| `1,000` | `D1_read_taxon_dossier` | `mongodb` | `0.541` | **`0.604`** | `0.640` | **`0.900`** | `1.072` | **`1,561.96`** |
| `1,000` | `D1_read_taxon_dossier` | `couchdb` | `1.650` | `2.032` | `2.185` | `2.829` | `3.525` | `457.59` |
| `1,000` | `D2_nested_attribute_query` | `mongodb` | `0.830` | **`0.981`** | `1.016` | **`1.389`** | `1.457` | **`984.58`** |
| `1,000` | `D2_nested_attribute_query` | `couchdb` | `11.218` | `15.697` | `14.751` | `16.946` | `17.170` | `67.79` |
| `1,000` | `D3_versioned_dossier_update` | `mongodb` | `1.917` | **`2.135`** | `2.206` | **`2.634`** | `2.747` | **`453.22`** |
| `1,000` | `D3_versioned_dossier_update` | `couchdb` | `11.797` | `13.075` | `13.042` | `14.090` | `14.719` | `76.68` |
| `1,000` | `D4_bulk_raw_source_insert` | `mongodb` | `1.142` | **`1.315`** | `1.483` | **`2.211`** | `3.718` | **`674.23`** |
| `1,000` | `D4_bulk_raw_source_insert` | `couchdb` | `8.212` | `9.018` | `9.187` | `10.270` | `10.571` | `108.85` |
| `10,000` | `D1_read_taxon_dossier` | `mongodb` | `0.597` | **`0.658`** | `0.779` | **`1.287`** | `2.070` | **`1,282.93`** |
| `10,000` | `D1_read_taxon_dossier` | `couchdb` | `1.807` | `3.345` | `3.491` | `5.293` | `9.395` | `286.41` |
| `10,000` | `D2_nested_attribute_query` | `mongodb` | `0.809` | **`0.985`** | `1.040` | **`1.293`** | `1.303` | **`962.01`** |
| `10,000` | `D2_nested_attribute_query` | `couchdb` | `7.898` | `12.411` | `25.878` | **`60.228`** | **`66.243`** | `38.64` |
| `10,000` | `D3_versioned_dossier_update` | `mongodb` | `1.848` | **`2.098`** | `2.237` | **`3.082`** | `3.523` | **`447.11`** |
| `10,000` | `D3_versioned_dossier_update` | `couchdb` | `12.722` | `14.017` | `14.148` | `16.711` | `17.238` | `70.68` |
| `10,000` | `D4_bulk_raw_source_insert` | `mongodb` | `1.147` | **`1.291`** | `1.409` | **`1.929`** | `3.523` | **`709.57`** |
| `10,000` | `D4_bulk_raw_source_insert` | `couchdb` | `8.308` | `9.348` | `9.369` | `10.558` | `11.230` | `106.74` |
| `50,000` | `D1_read_taxon_dossier` | `mongodb` | `0.472` | **`0.562`** | `0.569` | **`0.629`** | `0.912` | **`1,757.46`** |
| `50,000` | `D1_read_taxon_dossier` | `couchdb` | `2.195` | `3.554` | `3.966` | `5.018` | `14.468` | `252.17` |
| `50,000` | `D2_nested_attribute_query` | `mongodb` | `0.729` | **`0.864`** | `0.947` | **`1.220`** | `1.692` | **`1,056.08`** |
| `50,000` | `D2_nested_attribute_query` | `couchdb` | `10.097` | `12.432` | `28.662` | **`66.207`** | **`67.085`** | `34.89` |
| `50,000` | `D3_versioned_dossier_update` | `mongodb` | `1.550` | **`1.831`** | `1.894` | **`2.320`** | `2.712` | **`527.96`** |
| `50,000` | `D3_versioned_dossier_update` | `couchdb` | `15.959` | `17.670` | `23.331` | `43.944` | `47.930` | `42.86` |
| `50,000` | `D4_bulk_raw_source_insert` | `mongodb` | `0.943` | **`1.121`** | `1.192` | **`1.372`** | `2.688` | **`838.79`** |
| `50,000` | `D4_bulk_raw_source_insert` | `couchdb` | `10.554` | `11.930` | `16.552` | `32.021` | `37.331` | `60.41` |

### 4.3 Análisis comparativo documental
- **Superioridad de latencia, carga y CPU en MongoDB `8.0.38`:** en `50,000` registros crudos, MongoDB cargó en `773.56 ms` frente a `5,015.91 ms` en CouchDB (`6.5×` más rápido), mantuvo CPU pico de apenas `29.47%` frente a `196.53%` (saturación de los 2 núcleos) en CouchDB, y superó a CouchDB en las 4 operaciones: `6.3×` menor `p50` en `D1`, **`14.4×`** en `D2` (`54.3×` menor `p95`), `9.6×` en `D3` y `10.6×` en `D4`. La existencia del índice multikey `idx_claims_nested` y del protocolo binario BSON explica la estabilidad de MongoDB frente al protocolo HTTP/JSON y al escaneo `_all_docs` observado en las iteraciones `SYN_PRODUCER` de CouchDB (`results/raw/20261121T044412Z_bench_couchdb_c198d9.csv`).
- **Aspectos donde CouchDB `3.5.3` mostró ventaja o debe matizarse:** CouchDB mantuvo menor pico de RAM observado (`169.40`–`212.80 MiB` vs `269.90`–`418.20 MiB` en MongoDB) y conserva una licencia **Apache 2.0** frente a la **SSPL** de MongoDB Community. Asimismo, la colección `taxon_dossiers` no creció entre `10k` y `50k` (`1,300` docs), por lo que la ventaja de `D1`–`D3` refleja rendimiento en `1,300` expedientes con crecimiento de `50,000` documentos en `raw_source_records`.

---

## 5. Experimentos Orientados a Grafos (`Neo4j 2026.10.2` vs. `Memgraph 3.14.0`) — Fase 2

**Respaldo documental original:**  
- `1,000`: `results/summaries/20261121T044048Z_bench_neo4j_7dc3b7.json`, `20261121T044111Z_bench_memgraph_8e3dac.json`, `reports/20261121T044122Z_compare_graph_c95581.md`.  
- `10,000`: `results/summaries/20261121T043542Z_bench_neo4j_f70d79.json`, `20261121T043610Z_bench_memgraph_e7804e.json`, `reports/20261121T043701Z_compare_graph_9624da.md`.  
- `50,000`: `results/summaries/20261121T044507Z_bench_neo4j_a63d11.json`, `20261121T044548Z_bench_memgraph_118693.json`, `reports/20261121T050159Z_compare_graph_e18c84.md` y bitácora `results/logs/20261121T044507Z_bench_neo4j_a63d11.log`.

### 5.1 Fases de ciclo de vida, memoria, CPU y métricas reportadas (límite `1,024.0 MiB`)

| Volumen (`PUBLISHED`) | Motor | Conexión (ms) | Esquema (ms) | Carga (ms) | Índices (ms) | Limpieza (ms) | Pico RAM (MiB) | Prom. RAM (MiB) | Pico CPU (%) | `OOM` | Métrica `storage_bytes` *(NO comparable)* |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `1,000` (`838`) | `neo4j` | `110.28` | `255.88` | `1,951.32` | `124.64` | `193.03` | `788.00` | `756.45` | `196.01` | `False` | `1,950` **(conteo de nodos, NO bytes)** |
| `1,000` (`838`) | `memgraph` | `2.41` | `41.86` | `645.50` | `7.48` | `6.50` | `125.90` | `117.15` | `86.62` | `False` | `109,156,761` **(`memory_tracked` en RAM)** |
| `10,000` (`8,475`) | `neo4j` | `133.53` | `269.50` | `4,815.78` | `57.97` | `1,079.25` | `816.50` | `794.26` | `195.44` | `False` | `18,332` **(conteo de nodos, NO bytes)** |
| `10,000` (`8,475`) | `memgraph` | `20.57` | `9.21` | **`40,411.49`** | `16.51` | `61.77` | `143.20` | `116.04` | `101.50` | `False` | `98,283,028` **(`memory_tracked` en RAM)** |
| `50,000` (`42,523`) | `neo4j` | `112.40` | `252.12` | `13,839.91` | `55.44` | **`0.00` (FALLÓ)** | **`934.20`** | `769.83` | `198.38` | `False` | `86,428` **(conteo de nodos, NO bytes)** |
| `50,000` (`42,523`) | `memgraph` | `2.42` | `9.42` | **`954,975.00`** (`~15m 55s`) | `60.51` | `448.95` | `191.20` | `118.01` | `123.26` | `False` | `154,843,217` **(`memory_tracked` en RAM)** |

> **Fallo explícito registrado en `20261121T044507Z_bench_neo4j_a63d11.json` y `.log`:** tras completar con `100.00%` de éxito la carga y las 140 ejecuciones de `G1`–`G4`, la fase `cleanup_test_data` falló con `TransientError: {neo4j_code: Neo.TransientError.General.MemoryPoolOutOfMemoryError} {message: The allocation of an extra 2.0 MiB would use more than the limit 268.8 MiB. Currently using 267.0 MiB. dbms.memory.transaction.total.max threshold reached}`. El contenedor no fue terminado por el kernel (`OOMKilled: False`), pero alcanzó **`934.20 MiB`** (`91.2%` del techo `1,024 MiB`).

### 5.2 Latencias por operación (`warmup = 5`, `n = 30`, `100.00%` corrección, `0` errores durante workloads)

| Volumen | Operación | Motor | `min` (ms) | `p50` (ms) | `mean` (ms) | `p95` (ms) | `max` (ms) | `ops/s` (monohilo) |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| `1,000` | `G1_taxon_neighbors` | `neo4j` | `6.065` | `8.583` | `9.491` | `16.074` | `21.576` | `105.36` |
| `1,000` | `G1_taxon_neighbors` | `memgraph` | `1.405` | **`1.753`** | `1.855` | **`2.296`** | `2.490` | **`539.09`** |
| `1,000` | `G2_filtered_subgraph` | `neo4j` | `3.762` | `5.369` | `5.704` | `9.958` | `14.087` | `175.31` |
| `1,000` | `G2_filtered_subgraph` | `memgraph` | `1.075` | **`1.655`** | `1.785` | **`2.475`** | `3.136` | **`560.35`** |
| `1,000` | `G3_distinct_partner_count` | `neo4j` | `4.314` | `4.857` | `5.112` | `6.050` | `10.713` | `195.62` |
| `1,000` | `G3_distinct_partner_count` | `memgraph` | `1.257` | **`1.423`** | `2.092` | **`1.789`** | `20.605` | **`477.95`** |
| `1,000` | `G4_idempotent_assertion_upsert` | `neo4j` | `4.482` | `5.968` | `6.701` | `12.717` | `15.380` | `149.23` |
| `1,000` | `G4_idempotent_assertion_upsert` | `memgraph` | `1.214` | **`1.444`** | `1.529` | **`2.057`** | `2.496` | **`654.00`** |
| `10,000` | `G1_taxon_neighbors` | `neo4j` | `15.061` | `16.550` | `19.078` | `26.668` | `41.412` | `52.42` |
| `10,000` | `G1_taxon_neighbors` | `memgraph` | `6.492` | **`7.070`** | `7.094` | **`7.654`** | `8.358` | **`140.97`** |
| `10,000` | `G2_filtered_subgraph` | `neo4j` | `6.865` | `7.752` | `8.567` | `12.596` | `23.161` | `116.72` |
| `10,000` | `G2_filtered_subgraph` | `memgraph` | `3.328` | **`4.020`** | `4.019` | **`4.479`** | `5.050` | **`248.81`** |
| `10,000` | `G3_distinct_partner_count` | `neo4j` | `15.194` | `16.533` | `17.882` | `23.975` | `36.120` | `55.92` |
| `10,000` | `G3_distinct_partner_count` | `memgraph` | `6.046` | **`6.435`** | `6.537` | **`7.093`** | `9.149` | **`152.97`** |
| `10,000` | `G4_idempotent_assertion_upsert` | `neo4j` | `4.233` | `5.433` | `6.561` | `12.721` | `24.913` | `152.42` |
| `10,000` | `G4_idempotent_assertion_upsert` | `memgraph` | `3.387` | **`3.597`** | `3.667` | **`4.057`** | `4.197` | **`272.71`** |
| `50,000` | `G1_taxon_neighbors` | `neo4j` | `52.385` | `54.597` | `55.111` | `58.400` | `63.644` | `18.15` |
| `50,000` | `G1_taxon_neighbors` | `memgraph` | `36.000` | **`38.853`** | `39.996` | **`45.499`** | `51.703` | **`25.00`** |
| `50,000` | `G2_filtered_subgraph` | `neo4j` | `11.041` | **`12.944`** | `13.207` | **`15.975`** | `18.171` | **`75.71`** |
| `50,000` | `G2_filtered_subgraph` | `memgraph` | `9.969` | `16.674` | `17.682` | `25.898` | `28.038` | `56.56` |
| `50,000` | `G3_distinct_partner_count` | `neo4j` | `67.672` | `70.802` | `71.382` | `78.250` | `80.970` | `14.01` |
| `50,000` | `G3_distinct_partner_count` | `memgraph` | `30.456` | **`32.575`** | `32.783` | **`34.645`** | `36.279` | **`30.50`** |
| `50,000` | `G4_idempotent_assertion_upsert` | `neo4j` | `3.692` | **`4.823`** | `5.262` | **`9.505`** | `14.276` | **`190.03`** |
| `50,000` | `G4_idempotent_assertion_upsert` | `memgraph` | `14.075` | `15.340` | `15.512` | `16.886` | `17.005` | `64.47` |

### 5.3 Análisis comparativo orientado a grafos (balance objetivo de ventajas y desventajas)
- **Rendimiento de consultas vs. ingestión:** Memgraph `3.14.0` superó a Neo4j en todas las latencias a `1,000` y `10,000`, y en `50,000` conservó ventaja en recorrido de vecindario (`G1` p50 `38.85 ms` vs `54.60 ms`) y conteo de socios (`G3` p50 `32.58 ms` vs `70.80 ms`), con un pico de RAM mucho menor (`191.20 MiB` vs `934.20 MiB`). Sin embargo, **Neo4j superó a Memgraph en `50,000` en las dos operaciones más críticas para la arquitectura Outbox de BioLink**: subgrafo filtrado (`G2` p50 `12.944 ms` vs `16.674 ms`) y *upsert* idempotente de proyección (`G4` p50 `4.823 ms` vs `15.340 ms`, `2.95×` mayor throughput).
- **Cuello de botella de carga en Memgraph (`954,975.00 ms` = `15 min 55 s` en `50k` vs `13,839.91 ms` en Neo4j):** este costo superlineal (`69×` mayor que Neo4j en `50k`) invalidó la viabilidad operativa inmediata de Memgraph bajo la configuración probada del benchmark, ya que consumió por sí solo el `58.6%` del tiempo total de toda la campaña de 18 corridas (`27 min 19 s`), debido a que en Memgraph los constraints creados en `prepare_schema()` no crean índices de consulta antes de `load_dataset()`.
- **Riesgo de memoria en Neo4j:** el experimento demostró que Neo4j consumió **`934.20 MiB`** de los `1,024 MiB` asignados en `50k` (`816.50 MiB` ya en `10k`) y agotó el pool transaccional (`267.0 / 268.8 MiB`) al ejecutar `DETACH DELETE` por lotes de `2,000` nodos (`cleanup_test_data`), exponiendo un riesgo operativo real cuando se requiere retirar o reconciliar grafos grandes bajo presupuesto de `1 GiB`.

---

## 6. Justificación de la Selección Final y Límites de lo Demostrado

| Paradigma | Preselección preliminar Etapa 3 (`03_matriz_comparativa_motores_biolink.csv`) | Motor seleccionado en `biolink-backend` | Evidencia empírica que justifica la elección | Ventajas demostradas | Limitaciones y mitigaciones exigidas (qué NO resuelve el benchmark por sí solo) |
|---|---|---|---|---|---|
| **Relacional (SSOT + Outbox)** | Primera opción: MySQL `8.4 LTS` *(PostgreSQL `18.7` como alternativa)* | **PostgreSQL `18.7`** (`postgres:18.7`) | Cambio de decisión **directamente justificado por el benchmark**: en `1k`–`50k`, PostgreSQL redujo **4.9×** el pico de RAM (`124.80` vs `614.80 MiB`), fue superior en búsqueda (`R1`), transacciones Outbox con `JSONB` (`R3`), lotes (`R4`), carga e indexación. | Huella base mínima (`< 17%` de `768 MiB`), mejor rendimiento en transacciones Outbox (`340.64 ops/s` en 50k), `JSONB` nativo, licencia permisiva. | El benchmark evidenció **degradación de `R2` en 50k (`6.727 ms`)** y **limpieza lenta (`88.95 s`)**. La selección asume mitigación física mediante índice parcial cubriente `idx_assertion_published_r2_covering` (`002_create_indexes.sql`) e índices sobre FKs, cuya ganancia específica en latency queda pendiente de re-validación empírica. |
| **Documental (`taxon_dossier`, `study_dossier`, `raw_source_record`)** | Primera opción: MongoDB `8.0.38` | **MongoDB Community `8.0.38`** (`mongo:8.0.38`) | **Confirmado rotundamente** en todos los volúmenes (`1k`, `10k`, `50k`): menor latencia en `D1`–`D4` (`6.3×` a `14.4×` mejor p50 en 50k), `6.5×` menor tiempo de carga en 50k y `6.7×` menor CPU pico (`29.47%` vs `196.53%`). | Consultas sobre arreglos anidados `claims` con latencia sub-milisegundo (`D2` p50 `0.864 ms`), estabilidad extrema (`p95 <= 2.32 ms` en 50k) gracias a `$elemMatch` indexado y esquema `$jsonSchema`. | Mayor consumo de RAM en frío (`407`–`418 MiB` en 1k/10k con techo `256 MiB` WiredTiger), aunque bajo el límite `768 MiB`. Su licencia **SSPL** impone restricción legal ante distribución como servicio comercial gestionado (no relevante para despliegue académico interno). |
| **Grafo (proyección solo `PUBLISHED`)** | Primera opción: Neo4j Community | **Neo4j Community `2026.10.2`** (`neo4j:2026.10.2-community`) | **Confirmado con reservas operativas explícitas:** superó a Memgraph en carga a `50k` (`13.84 s` vs `15.92 min`), en subgrafo filtrado `G2` (`12.944 ms` vs `16.674 ms`) y en *upsert* idempotente `G4` clave para `OutboxProjectionWorker` (`4.823 ms` vs `15.340 ms`). | Estabilidad de ingesta `UNWIND ... MERGE` sin degradación cuadrática, mejor rendimiento en `G2` y `G4` en 50k, persistencia en disco nativa por defecto sin depender de toda la base en RAM. | Menor velocidad en `G1`/`G3` a 50k que Memgraph, consumo RAM elevado (`934.20 / 1,024 MiB`), fallo `MemoryPoolOutOfMemoryError` al borrar lotes de `2,000` nodos, y restricción Community de **1 base de usuario**. Obligó en `biolink-backend` a acotar explícitamente `NEO4J_TX_TOTAL_MAX=256m`, `NEO4J_TX_MAX=64m` y retiros en lotes `IN TRANSACTIONS OF 1000 ROWS`, configuración aún pendiente de re-testear en `50k` en benchmark. |

### Conclusión global acotada a la evidencia
Los resultados experimentales de `biolink-benchmarking` **justifican suficientemente** sustituir MySQL por **PostgreSQL 18.7** y confirmar a **MongoDB 8.0.38** bajo la arquitectura híbrida de BioLink dentro de un techo de `4,096 MiB` (`124.80 MiB + 269.90 MiB` observados en carga de 50k). En el paradigma de grafos, **Neo4j 2026.10.2-community** resulta la opción **más compatible operativamente con el patrón Outbox y persistencia en disco**, frente al tiempo prohibitivo de carga de Memgraph en 50k (`954.98 s`), pero dicha elección solo es sostenible manteniendo **Neo4j como proyección derivada no autoritativa y aplicando cuotas transaccionales explícitas** (`<= 1,024 MiB` totales y eliminación en micro-lotes), dado que el benchmark demostró vulnerabilidad de memoria transaccional en limpiezas masivas y latencia inferior a Memgraph en consultas `G1` y `G3`.
