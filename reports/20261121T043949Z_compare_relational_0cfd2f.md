# Comparativa secuencial — Modelo relational (`20261121T043949Z_compare_relational_0cfd2f`)

- **Dataset:** `synthetic_1000_seed_20261120` (semilla `20261120`)
- **Candidatos:** `mysql` vs. `postgresql`

| Motor | Versión | Conexión (ms) | Carga (ms) | Índices (ms) | Pico RAM (MiB) | OOMKilled | Almacenamiento (bytes) |
|---|---|---:|---:|---:|---:|---|---:|
| `mysql` | `8.4.13` | 55.41 | 815.28 | 241.94 | 503.6 | False | 2031616 |
| `postgresql` | `18.7 (Debian 18.7-1.pgdg13+5)` | 33.79 | 157.20 | 10.50 | 73.92 | False | 10991295 |

## Detalle por operación

| Motor | Operación | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---|---:|---:|---:|---:|---:|---:|
| `mysql` | `R1_taxon_search` | 2.260 | 4.218 | 5.949 | 424.84 | 100.00% | 0 |
| `mysql` | `R2_filtered_assertions` | 2.488 | 3.971 | 4.269 | 358.57 | 100.00% | 0 |
| `mysql` | `R3_transactional_assertion_outbox` | 7.297 | 21.669 | 23.026 | 98.54 | 100.00% | 0 |
| `mysql` | `R4_batch_import_insert` | 9.965 | 25.497 | 27.426 | 76.39 | 100.00% | 0 |
| `postgresql` | `R1_taxon_search` | 0.453 | 0.673 | 1.111 | 2051.82 | 100.00% | 0 |
| `postgresql` | `R2_filtered_assertions` | 0.774 | 1.174 | 1.290 | 1274.35 | 100.00% | 0 |
| `postgresql` | `R3_transactional_assertion_outbox` | 2.970 | 4.415 | 5.217 | 313.16 | 100.00% | 0 |
| `postgresql` | `R4_batch_import_insert` | 3.563 | 4.011 | 4.205 | 288.82 | 100.00% | 0 |
