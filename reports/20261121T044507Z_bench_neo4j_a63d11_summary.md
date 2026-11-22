# Resumen de ejecución: `20261121T044507Z_bench_neo4j_a63d11`

- **Modo:** `benchmark`
- **Motor:** `neo4j` (graph)
- **Dataset:** `synthetic_50000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:45:07Z`
- **Fin UTC:** `2026-11-21T04:45:44Z`
- **Conexión (ms):** `112.402` | **Esquema (ms):** `252.124` | **Carga (ms):** `13839.914` | **Índices (ms):** `55.445`
- **Almacenamiento reportado (bytes):** `86428`
- **Pico memoria Docker (MiB):** `934.2` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `G1_taxon_neighbors` | 30 | 54.597 | 58.400 | 63.644 | 18.15 | 100.00% | 0 |
| `G2_filtered_subgraph` | 30 | 12.944 | 15.975 | 18.171 | 75.71 | 100.00% | 0 |
| `G3_distinct_partner_count` | 30 | 70.802 | 78.250 | 80.970 | 14.01 | 100.00% | 0 |
| `G4_idempotent_assertion_upsert` | 30 | 4.823 | 9.505 | 14.276 | 190.03 | 100.00% | 0 |

## Errores registrados

- TransientError: {neo4j_code: Neo.TransientError.General.MemoryPoolOutOfMemoryError} {message: The allocation of an extra 2.0 MiB would use more than the limit 268.8 MiB. Currently using 267.0 MiB. dbms.memory.transaction.total.max threshold reached} {gql_status: 51N72} {gql_status_description: error: system configuration or operation exception - memory pool out of memory. Failed to allocate memory in a memory pool. See dbms.memory.transaction.total.max in the neo4j.conf file.}
