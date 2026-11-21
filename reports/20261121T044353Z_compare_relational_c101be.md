# Comparativa secuencial — Modelo relational (`20261121T044353Z_compare_relational_c101be`)

- **Dataset:** `synthetic_50000_seed_20261120` (semilla `20261120`)
- **Candidatos:** `mysql` vs. `postgresql`

| Motor | Versión | Conexión (ms) | Carga (ms) | Índices (ms) | Pico RAM (MiB) | OOMKilled | Almacenamiento (bytes) |
|---|---|---:|---:|---:|---:|---|---:|
| `mysql` | `8.4.13` | 19.40 | 8744.70 | 727.67 | 614.8 | False | 57638912 |
| `postgresql` | `18.7 (Debian 18.7-1.pgdg13+5)` | 31.93 | 6484.71 | 180.87 | 124.8 | False | 70915775 |

## Detalle por operación

| Motor | Operación | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---|---:|---:|---:|---:|---:|---:|
| `mysql` | `R1_taxon_search` | 1.255 | 1.549 | 1.654 | 774.01 | 100.00% | 0 |
| `mysql` | `R2_filtered_assertions` | 1.746 | 3.600 | 4.123 | 481.82 | 100.00% | 0 |
| `mysql` | `R3_transactional_assertion_outbox` | 5.280 | 7.954 | 9.484 | 180.64 | 100.00% | 0 |
| `mysql` | `R4_batch_import_insert` | 4.935 | 5.925 | 6.746 | 197.95 | 100.00% | 0 |
| `postgresql` | `R1_taxon_search` | 0.520 | 0.694 | 1.014 | 1790.56 | 100.00% | 0 |
| `postgresql` | `R2_filtered_assertions` | 6.727 | 9.403 | 9.880 | 157.90 | 100.00% | 0 |
| `postgresql` | `R3_transactional_assertion_outbox` | 2.797 | 3.868 | 4.568 | 340.64 | 100.00% | 0 |
| `postgresql` | `R4_batch_import_insert` | 3.185 | 3.805 | 5.855 | 307.60 | 100.00% | 0 |
