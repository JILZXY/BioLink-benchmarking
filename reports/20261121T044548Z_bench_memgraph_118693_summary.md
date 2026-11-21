# Resumen de ejecución: `20261121T044548Z_bench_memgraph_118693`

- **Modo:** `benchmark`
- **Motor:** `memgraph` (graph)
- **Dataset:** `synthetic_50000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:45:48Z`
- **Fin UTC:** `2026-11-21T05:01:57Z`
- **Conexión (ms):** `2.416` | **Esquema (ms):** `9.417` | **Carga (ms):** `954974.996` | **Índices (ms):** `60.510`
- **Almacenamiento reportado (bytes):** `154843217`
- **Pico memoria Docker (MiB):** `191.2` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `G1_taxon_neighbors` | 30 | 38.853 | 45.499 | 51.703 | 25.00 | 100.00% | 0 |
| `G2_filtered_subgraph` | 30 | 16.674 | 25.898 | 28.038 | 56.56 | 100.00% | 0 |
| `G3_distinct_partner_count` | 30 | 32.575 | 34.645 | 36.279 | 30.50 | 100.00% | 0 |
| `G4_idempotent_assertion_upsert` | 30 | 15.340 | 16.886 | 17.005 | 64.47 | 100.00% | 0 |
