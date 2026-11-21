# Resumen de ejecución: `20261121T044136Z_bench_mysql_a62a14`

- **Modo:** `benchmark`
- **Motor:** `mysql` (relational)
- **Dataset:** `synthetic_50000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:41:36Z`
- **Fin UTC:** `2026-11-21T04:42:05Z`
- **Conexión (ms):** `19.399` | **Esquema (ms):** `555.543` | **Carga (ms):** `8744.704` | **Índices (ms):** `727.669`
- **Almacenamiento reportado (bytes):** `57638912`
- **Pico memoria Docker (MiB):** `614.8` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `R1_taxon_search` | 30 | 1.255 | 1.549 | 1.654 | 774.01 | 100.00% | 0 |
| `R2_filtered_assertions` | 30 | 1.746 | 3.600 | 4.123 | 481.82 | 100.00% | 0 |
| `R3_transactional_assertion_outbox` | 30 | 5.280 | 7.954 | 9.484 | 180.64 | 100.00% | 0 |
| `R4_batch_import_insert` | 30 | 4.935 | 5.925 | 6.746 | 197.95 | 100.00% | 0 |
