# Catálogo de Workloads y Correspondencia con `OP-01` a `OP-15`

Todos los workloads están implementados en `src/biolink_bench/workloads/` y ejecutan consultas equivalentes dentro de cada paradigma de base de datos usando únicamente drivers nativos. Los nombres y parámetros de consulta se construyen de forma determinista desde el `DatasetBundle` cargado para que ambos candidatos de una misma categoría reciban exactamente la misma carga lógica.

---

## 1. Modelo Relacional (`MySQL 8.4 LTS` vs. `PostgreSQL 18.7`)

Implementación: `workloads/relational.py`, `drivers/relational/mysql_adapter.py`, `drivers/relational/postgresql_adapter.py`.

| Workload | Operaciones BioLink | Tipo | Descripción técnica | Validación automática |
|---|---|---|---|---|
| `R1_taxon_search` | `OP-01` | Lectura | Búsqueda por nombre exacto en `taxon_name` (mezclando nombres aceptados y sinónimos) con `JOIN` a `taxon`. | Conjunto exacto de `taxon_id` esperado según `bundle.taxon_names`. |
| `R2_filtered_assertions` | `OP-03`, `OP-05` | Lectura | Consulta filtrada de `interaction_assertion` por `locality_id`, `period_start >= X` y `status = 'PUBLISHED'`, ordenada y paginada (`LIMIT 50`). | Lista exacta y ordenada de `assertion_id`; verifica cero fugas de estados no publicados. |
| `R3_transactional_assertion_outbox` | `OP-11`, `OP-12` | Escritura ACID | Transacción única (`COMMIT`/`ROLLBACK`) que inserta `evidence`, `interaction_assertion` (`PUBLISHED`), `assertion_evidence`, `review_event` y `outbox_event` (`PENDING`). | Confirmación de transacción completa y coincidencia exacta de los 4 IDs generados. |
| `R4_batch_import_insert` | `OP-09`, `OP-10` | Escritura por lote | Inserción transaccional de 1 `import_batch` y lote de `50` registros `import_record` mediante `executemany`. | Conteo exacto `inserted_records == 50` e `import_batch_id` esperado. |

---

## 2. Modelo Documental (`MongoDB Community 8.0` vs. `Apache CouchDB 3.5.3`)

Implementación: `workloads/document.py`, `drivers/document/mongodb_adapter.py`, `drivers/document/couchdb_adapter.py`.

| Workload | Operaciones BioLink | Tipo | Descripción técnica | Validación automática |
|---|---|---|---|---|
| `D1_read_taxon_dossier` | `OP-02` | Lectura puntual | Lectura directa de `taxon_dossier` por `_id`/`taxon_id` (`find_one` en MongoDB; `GET /{db}/{id}` en CouchDB). | Coincidencia de `taxon_id` y conteo mínimo esperado de `claims`. |
| `D2_nested_attribute_query` | `OP-02`, `OP-13` | Lectura anidada | Búsqueda por arreglo anidado `claims` usando `$elemMatch` (`field = 'ecology.diet'`, `value = ...`) filtrada por `dataset_tag`. | Lista ordenada exacta de `taxon_id` coincidentes en memoria. |
| `D3_versioned_dossier_update` | `OP-13` | Escritura versionada | Lee el documento vigente, archiva una copia inmutable en `taxon_dossier_versions` (`{taxon_id}::v{old}`) e incrementa `document_version` añadiendo un `claim` en `taxon_dossiers` (respetando `_rev` en CouchDB). | Verifica `new_version == previous_version + 1` para el `taxon_id` objetivo. |
| `D4_bulk_raw_source_insert` | `OP-09`, `OP-10` | Escritura masiva | Inserción por lote de `50` documentos `raw_source_record` (`insert_many` en MongoDB; `POST /_bulk_docs` en CouchDB). | Verifica `inserted_count == 50`. |

---

## 3. Modelo de Grafo (`Neo4j Community` vs. `Memgraph Community`)

Implementación: `workloads/graph.py`, `drivers/graph/neo4j_adapter.py`, `drivers/graph/memgraph_adapter.py`.

| Workload | Operaciones BioLink | Tipo | Descripción técnica | Validación automática |
|---|---|---|---|---|
| `G1_taxon_neighbors` | `OP-03` | Lectura de vecindario | Recorrido `(Taxon)-[:ACTOR_IN]->(InteractionAssertion {status:'PUBLISHED'})-[:TARGETS]->(Taxon)` y localidad asociada para obtener contrapartes de un `taxon_id`. | Conjunto exacto de tuplas `(assertion_id, partner_taxon_id)` de `bundle.published_assertions`. |
| `G2_filtered_subgraph` | `OP-05` | Lectura de subgrafo | Subgrafo filtrado por `locality_id`, `interaction_type_code`, `period_start >= X` y `status = 'PUBLISHED'`. | Lista exacta de `assertion_id` y verificación de no mezcla de localidades. |
| `G3_distinct_partner_count` | `OP-07` | Lectura analítica | Conteo separado de taxones contraparte distintos (`count(DISTINCT partner_id)`) y afirmaciones (`count(DISTINCT assertion_id)`). | Coincidencia exacta de `distinct_partner_count` y `assertion_count`. |
| `G4_idempotent_assertion_upsert` | `OP-12` | Escritura idempotente | `MERGE` por `assertion_id` enlazando `Taxon`, `Locality`, `Evidence` y `Source`; la mitad de iteraciones repite un `assertion_id` previo para comprobar idempotencia real sin duplicación. | Verifica retorno de `assertion_id` esperado y estado `PUBLISHED`. |

---

## 4. Cobertura explícita respecto al catálogo completo `OP-01` a `OP-15`

| Operación BioLink | Cobertura en workloads | Observación |
|---|---|---|
| `OP-01` Buscar taxones | `R1_taxon_search` | Cubierta en el paradigma relacional (fuente de verdad taxonómica). |
| `OP-02` Consultar ficha de taxón | `D1_read_taxon_dossier`, `D2_nested_attribute_query` | Cubierta en el paradigma documental. |
| `OP-03` Listar interacciones de un taxón | `R2_filtered_assertions`, `G1_taxon_neighbors` | Cubierta en relacional y grafo. |
| `OP-04` Consultar detalle/evidencia | Verificada en esquema y relaciones (`evidence`, `study_dossier`, `Evidence->Source`) | Su ruta principal es combinación de `OP-02` + `OP-03`/`R2`. |
| `OP-05` Filtrar subred documentada | `R2_filtered_assertions`, `G2_filtered_subgraph` | Cubierta en relacional y grafo sin mezclar Montes Azules y PDLG. |
| `OP-06` Comparar localidades | Cubierta mediante parametrización separada por `locality_id` en `G2`/`R2` | La agregación comparativa de alto nivel corresponde a la futura lógica de `biolink-backend`. |
| `OP-07` Calcular conectividad descriptiva | `G3_distinct_partner_count` | Cubierta en grafo separando socios distintos de número de afirmaciones. |
| `OP-08` Consultar fuente o estudio | Almacenado en `source` (Relacional) y `study_dossier` (Documental) | Cubierta en carga y consulta estructural de esquema. |
| `OP-09` Registrar lote de importación | `R4_batch_import_insert`, `D4_bulk_raw_source_insert` | Cubierta en relacional y documental. |
| `OP-10` Validar y normalizar registro | `R4_batch_import_insert`, `D4_bulk_raw_source_insert` | Cubierta mediante `import_record` y `raw_source_record`. |
| `OP-11` Crear afirmación de interacción | `R3_transactional_assertion_outbox` | Cubierta junto a evidencia obligatoria. |
| `OP-12` Revisar/publicar y proyectar afirmación | `R3_transactional_assertion_outbox`, `G4_idempotent_assertion_upsert` | Cubierta en ambos extremos del patrón outbox → proyección. |
| `OP-13` Actualizar ficha de taxón | `D2_nested_attribute_query`, `D3_versioned_dossier_update` | Cubierta con historial inmutable de versiones. |
| `OP-14` Consultar historial de procedencia | Tablas `import_batch`, `import_record`, `review_event` y `taxon_dossier_versions` | Estructura cargada y auditable en el modelo. |
| `OP-15` Consultar ocurrencias | Separación estricta de presencia vs. interacción en fixture (`data_strategy.md`) | No se implementó tabla `occurrence` separada como workload prioritario de V1; la regla de no inferencia está validada en el fixture científico. |
