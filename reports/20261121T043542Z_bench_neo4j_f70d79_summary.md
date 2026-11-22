# Resumen de ejecución: `20261121T043542Z_bench_neo4j_f70d79`

- **Modo:** `benchmark`
- **Motor:** `neo4j` (graph)
- **Dataset:** `synthetic_10000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:35:42Z`
- **Fin UTC:** `2026-11-21T04:36:06Z`
- **Conexión (ms):** `133.527` | **Esquema (ms):** `269.504` | **Carga (ms):** `4815.783` | **Índices (ms):** `57.968`
- **Almacenamiento reportado (bytes):** `18332`
- **Pico memoria Docker (MiB):** `816.5` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `G1_taxon_neighbors` | 30 | 16.550 | 26.668 | 41.412 | 52.42 | 100.00% | 0 |
| `G2_filtered_subgraph` | 30 | 7.752 | 12.596 | 23.161 | 116.72 | 100.00% | 0 |
| `G3_distinct_partner_count` | 30 | 16.533 | 23.975 | 36.120 | 55.92 | 100.00% | 0 |
| `G4_idempotent_assertion_upsert` | 30 | 5.433 | 12.721 | 24.913 | 152.42 | 100.00% | 0 |
