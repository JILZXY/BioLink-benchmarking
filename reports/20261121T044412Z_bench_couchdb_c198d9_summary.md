# Resumen de ejecución: `20261121T044412Z_bench_couchdb_c198d9`

- **Modo:** `benchmark`
- **Motor:** `couchdb` (document)
- **Dataset:** `synthetic_50000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:44:12Z`
- **Fin UTC:** `2026-11-21T04:44:37Z`
- **Conexión (ms):** `110.984` | **Esquema (ms):** `70.341` | **Carga (ms):** `5015.910` | **Índices (ms):** `40.785`
- **Almacenamiento reportado (bytes):** `40487769`
- **Pico memoria Docker (MiB):** `212.8` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `D1_read_taxon_dossier` | 30 | 3.554 | 5.018 | 14.468 | 252.17 | 100.00% | 0 |
| `D2_nested_attribute_query` | 30 | 12.432 | 66.207 | 67.085 | 34.89 | 100.00% | 0 |
| `D3_versioned_dossier_update` | 30 | 17.670 | 43.944 | 47.930 | 42.86 | 100.00% | 0 |
| `D4_bulk_raw_source_insert` | 30 | 11.930 | 32.021 | 37.331 | 60.41 | 100.00% | 0 |
