# Resumen de ejecución: `20261121T044206Z_bench_postgresql_530dc1`

- **Modo:** `benchmark`
- **Motor:** `postgresql` (relational)
- **Dataset:** `synthetic_50000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:42:06Z`
- **Fin UTC:** `2026-11-21T04:43:52Z`
- **Conexión (ms):** `31.926` | **Esquema (ms):** `24.289` | **Carga (ms):** `6484.708` | **Índices (ms):** `180.867`
- **Almacenamiento reportado (bytes):** `70915775`
- **Pico memoria Docker (MiB):** `124.8` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `R1_taxon_search` | 30 | 0.520 | 0.694 | 1.014 | 1790.56 | 100.00% | 0 |
| `R2_filtered_assertions` | 30 | 6.727 | 9.403 | 9.880 | 157.90 | 100.00% | 0 |
| `R3_transactional_assertion_outbox` | 30 | 2.797 | 3.868 | 4.568 | 340.64 | 100.00% | 0 |
| `R4_batch_import_insert` | 30 | 3.185 | 3.805 | 5.855 | 307.60 | 100.00% | 0 |
