# Resumen de ejecución: `20261121T043920Z_bench_mysql_57c194`

- **Modo:** `benchmark`
- **Motor:** `mysql` (relational)
- **Dataset:** `synthetic_1000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:39:20Z`
- **Fin UTC:** `2026-11-21T04:39:37Z`
- **Conexión (ms):** `55.409` | **Esquema (ms):** `490.245` | **Carga (ms):** `815.281` | **Índices (ms):** `241.944`
- **Almacenamiento reportado (bytes):** `2031616`
- **Pico memoria Docker (MiB):** `503.6` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `R1_taxon_search` | 30 | 2.260 | 4.218 | 5.949 | 424.84 | 100.00% | 0 |
| `R2_filtered_assertions` | 30 | 2.488 | 3.971 | 4.269 | 358.57 | 100.00% | 0 |
| `R3_transactional_assertion_outbox` | 30 | 7.297 | 21.669 | 23.026 | 98.54 | 100.00% | 0 |
| `R4_batch_import_insert` | 30 | 9.965 | 25.497 | 27.426 | 76.39 | 100.00% | 0 |
