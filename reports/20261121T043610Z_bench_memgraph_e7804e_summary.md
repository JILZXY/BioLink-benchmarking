# Resumen de ejecución: `20261121T043610Z_bench_memgraph_e7804e`

- **Modo:** `benchmark`
- **Motor:** `memgraph` (graph)
- **Dataset:** `synthetic_10000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:36:10Z`
- **Fin UTC:** `2026-11-21T04:37:00Z`
- **Conexión (ms):** `20.573` | **Esquema (ms):** `9.212` | **Carga (ms):** `40411.486` | **Índices (ms):** `16.510`
- **Almacenamiento reportado (bytes):** `98283028`
- **Pico memoria Docker (MiB):** `143.2` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `G1_taxon_neighbors` | 30 | 7.070 | 7.654 | 8.358 | 140.97 | 100.00% | 0 |
| `G2_filtered_subgraph` | 30 | 4.020 | 4.479 | 5.050 | 248.81 | 100.00% | 0 |
| `G3_distinct_partner_count` | 30 | 6.435 | 7.093 | 9.149 | 152.97 | 100.00% | 0 |
| `G4_idempotent_assertion_upsert` | 30 | 3.597 | 4.057 | 4.197 | 272.71 | 100.00% | 0 |
