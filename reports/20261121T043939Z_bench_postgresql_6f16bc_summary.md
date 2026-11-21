# Resumen de ejecución: `20261121T043939Z_bench_postgresql_6f16bc`

- **Modo:** `benchmark`
- **Motor:** `postgresql` (relational)
- **Dataset:** `synthetic_1000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:39:39Z`
- **Fin UTC:** `2026-11-21T04:39:48Z`
- **Conexión (ms):** `33.786` | **Esquema (ms):** `30.961` | **Carga (ms):** `157.200` | **Índices (ms):** `10.501`
- **Almacenamiento reportado (bytes):** `10991295`
- **Pico memoria Docker (MiB):** `73.92` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `R1_taxon_search` | 30 | 0.453 | 0.673 | 1.111 | 2051.82 | 100.00% | 0 |
| `R2_filtered_assertions` | 30 | 0.774 | 1.174 | 1.290 | 1274.35 | 100.00% | 0 |
| `R3_transactional_assertion_outbox` | 30 | 2.970 | 4.415 | 5.217 | 313.16 | 100.00% | 0 |
| `R4_batch_import_insert` | 30 | 3.563 | 4.011 | 4.205 | 288.82 | 100.00% | 0 |
