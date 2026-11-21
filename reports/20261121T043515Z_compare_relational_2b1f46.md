# Comparativa secuencial — Modelo relational (`20261121T043515Z_compare_relational_2b1f46`)

- **Dataset:** `synthetic_10000_seed_20261120` (semilla `20261120`)
- **Candidatos:** `mysql` vs. `postgresql`

| Motor | Versión | Conexión (ms) | Carga (ms) | Índices (ms) | Pico RAM (MiB) | OOMKilled | Almacenamiento (bytes) |
|---|---|---:|---:|---:|---:|---|---:|
| `mysql` | `8.4.13` | 16.55 | 2850.00 | 615.95 | 547.6 | False | 1736704 |
| `postgresql` | `18.7 (Debian 18.7-1.pgdg13+5)` | 8.74 | 1366.70 | 62.30 | 91.7 | False | 23049919 |

## Detalle por operación

| Motor | Operación | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---|---:|---:|---:|---:|---:|---:|
| `mysql` | `R1_taxon_search` | 1.435 | 1.952 | 2.021 | 680.22 | 100.00% | 0 |
| `mysql` | `R2_filtered_assertions` | 1.659 | 2.222 | 3.021 | 570.33 | 100.00% | 0 |
| `mysql` | `R3_transactional_assertion_outbox` | 6.799 | 20.302 | 20.693 | 108.59 | 100.00% | 0 |
| `mysql` | `R4_batch_import_insert` | 6.022 | 20.116 | 20.820 | 115.76 | 100.00% | 0 |
| `postgresql` | `R1_taxon_search` | 0.501 | 0.660 | 1.042 | 1887.94 | 100.00% | 0 |
| `postgresql` | `R2_filtered_assertions` | 1.886 | 2.582 | 6.162 | 511.09 | 100.00% | 0 |
| `postgresql` | `R3_transactional_assertion_outbox` | 2.820 | 3.877 | 5.002 | 332.88 | 100.00% | 0 |
| `postgresql` | `R4_batch_import_insert` | 3.322 | 3.954 | 4.305 | 293.52 | 100.00% | 0 |
