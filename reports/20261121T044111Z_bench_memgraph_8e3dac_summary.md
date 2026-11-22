# Resumen de ejecución: `20261121T044111Z_bench_memgraph_8e3dac`

- **Modo:** `benchmark`
- **Motor:** `memgraph` (graph)
- **Dataset:** `synthetic_1000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:41:11Z`
- **Fin UTC:** `2026-11-21T04:41:20Z`
- **Conexión (ms):** `2.408` | **Esquema (ms):** `41.864` | **Carga (ms):** `645.504` | **Índices (ms):** `7.481`
- **Almacenamiento reportado (bytes):** `109156761`
- **Pico memoria Docker (MiB):** `125.9` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `G1_taxon_neighbors` | 30 | 1.753 | 2.296 | 2.490 | 539.09 | 100.00% | 0 |
| `G2_filtered_subgraph` | 30 | 1.655 | 2.475 | 3.136 | 560.35 | 100.00% | 0 |
| `G3_distinct_partner_count` | 30 | 1.423 | 1.789 | 20.605 | 477.95 | 100.00% | 0 |
| `G4_idempotent_assertion_upsert` | 30 | 1.444 | 2.057 | 2.496 | 654.00 | 100.00% | 0 |
