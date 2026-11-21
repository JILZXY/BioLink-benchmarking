# Resumen de ejecución: `20261121T043459Z_bench_postgresql_4cb5de`

- **Modo:** `benchmark`
- **Motor:** `postgresql` (relational)
- **Dataset:** `synthetic_10000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:34:59Z`
- **Fin UTC:** `2026-11-21T04:35:14Z`
- **Conexión (ms):** `8.744` | **Esquema (ms):** `24.757` | **Carga (ms):** `1366.697` | **Índices (ms):** `62.305`
- **Almacenamiento reportado (bytes):** `23049919`
- **Pico memoria Docker (MiB):** `91.7` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `R1_taxon_search` | 30 | 0.501 | 0.660 | 1.042 | 1887.94 | 100.00% | 0 |
| `R2_filtered_assertions` | 30 | 1.886 | 2.582 | 6.162 | 511.09 | 100.00% | 0 |
| `R3_transactional_assertion_outbox` | 30 | 2.820 | 3.877 | 5.002 | 332.88 | 100.00% | 0 |
| `R4_batch_import_insert` | 30 | 3.322 | 3.954 | 4.305 | 293.52 | 100.00% | 0 |
