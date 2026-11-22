# Resumen de ejecución: `20261121T044048Z_bench_neo4j_7dc3b7`

- **Modo:** `benchmark`
- **Motor:** `neo4j` (graph)
- **Dataset:** `synthetic_1000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:40:48Z`
- **Fin UTC:** `2026-11-21T04:41:07Z`
- **Conexión (ms):** `110.278` | **Esquema (ms):** `255.878` | **Carga (ms):** `1951.320` | **Índices (ms):** `124.636`
- **Almacenamiento reportado (bytes):** `1950`
- **Pico memoria Docker (MiB):** `788.0` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `G1_taxon_neighbors` | 30 | 8.583 | 16.074 | 21.576 | 105.36 | 100.00% | 0 |
| `G2_filtered_subgraph` | 30 | 5.369 | 9.958 | 14.087 | 175.31 | 100.00% | 0 |
| `G3_distinct_partner_count` | 30 | 4.857 | 6.050 | 10.713 | 195.62 | 100.00% | 0 |
| `G4_idempotent_assertion_upsert` | 30 | 5.968 | 12.717 | 15.380 | 149.23 | 100.00% | 0 |
