# Resumen de ejecución: `20261121T043440Z_bench_mysql_1693e5`

- **Modo:** `benchmark`
- **Motor:** `mysql` (relational)
- **Dataset:** `synthetic_10000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:34:40Z`
- **Fin UTC:** `2026-11-21T04:34:56Z`
- **Conexión (ms):** `16.551` | **Esquema (ms):** `49.552` | **Carga (ms):** `2850.001` | **Índices (ms):** `615.945`
- **Almacenamiento reportado (bytes):** `1736704`
- **Pico memoria Docker (MiB):** `547.6` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `R1_taxon_search` | 30 | 1.435 | 1.952 | 2.021 | 680.22 | 100.00% | 0 |
| `R2_filtered_assertions` | 30 | 1.659 | 2.222 | 3.021 | 570.33 | 100.00% | 0 |
| `R3_transactional_assertion_outbox` | 30 | 6.799 | 20.302 | 20.693 | 108.59 | 100.00% | 0 |
| `R4_batch_import_insert` | 30 | 6.022 | 20.116 | 20.820 | 115.76 | 100.00% | 0 |
