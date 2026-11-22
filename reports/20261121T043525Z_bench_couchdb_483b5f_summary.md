# Resumen de ejecución: `20261121T043525Z_bench_couchdb_483b5f`

- **Modo:** `benchmark`
- **Motor:** `couchdb` (document)
- **Dataset:** `synthetic_10000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:35:25Z`
- **Fin UTC:** `2026-11-21T04:35:40Z`
- **Conexión (ms):** `113.138` | **Esquema (ms):** `62.071` | **Carga (ms):** `1596.890` | **Índices (ms):** `25.719`
- **Almacenamiento reportado (bytes):** `9976076`
- **Pico memoria Docker (MiB):** `184.2` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `D1_read_taxon_dossier` | 30 | 3.345 | 5.293 | 9.395 | 286.41 | 100.00% | 0 |
| `D2_nested_attribute_query` | 30 | 12.411 | 60.228 | 66.243 | 38.64 | 100.00% | 0 |
| `D3_versioned_dossier_update` | 30 | 14.017 | 16.711 | 17.238 | 70.68 | 100.00% | 0 |
| `D4_bulk_raw_source_insert` | 30 | 9.348 | 10.558 | 11.230 | 106.74 | 100.00% | 0 |
