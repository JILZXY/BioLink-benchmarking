# Resumen de ejecución: `20261121T044029Z_bench_couchdb_00d5d2`

- **Modo:** `benchmark`
- **Motor:** `couchdb` (document)
- **Dataset:** `synthetic_1000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:40:29Z`
- **Fin UTC:** `2026-11-21T04:40:40Z`
- **Conexión (ms):** `127.264` | **Esquema (ms):** `65.459` | **Carga (ms):** `339.514` | **Índices (ms):** `26.230`
- **Almacenamiento reportado (bytes):** `2067380`
- **Pico memoria Docker (MiB):** `169.4` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `D1_read_taxon_dossier` | 30 | 2.032 | 2.829 | 3.525 | 457.59 | 100.00% | 0 |
| `D2_nested_attribute_query` | 30 | 15.697 | 16.946 | 17.170 | 67.79 | 100.00% | 0 |
| `D3_versioned_dossier_update` | 30 | 13.075 | 14.090 | 14.719 | 76.68 | 100.00% | 0 |
| `D4_bulk_raw_source_insert` | 30 | 9.018 | 10.270 | 10.571 | 108.85 | 100.00% | 0 |
