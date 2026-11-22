# Resumen de ejecución: `20261121T043515Z_bench_mongodb_b65cb2`

- **Modo:** `benchmark`
- **Motor:** `mongodb` (document)
- **Dataset:** `synthetic_10000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:35:15Z`
- **Fin UTC:** `2026-11-21T04:35:24Z`
- **Conexión (ms):** `29.408` | **Esquema (ms):** `62.937` | **Carga (ms):** `186.336` | **Índices (ms):** `162.661`
- **Almacenamiento reportado (bytes):** `229376`
- **Pico memoria Docker (MiB):** `418.2` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `D1_read_taxon_dossier` | 30 | 0.658 | 1.287 | 2.070 | 1282.93 | 100.00% | 0 |
| `D2_nested_attribute_query` | 30 | 0.985 | 1.293 | 1.303 | 962.01 | 100.00% | 0 |
| `D3_versioned_dossier_update` | 30 | 2.098 | 3.082 | 3.523 | 447.11 | 100.00% | 0 |
| `D4_bulk_raw_source_insert` | 30 | 1.291 | 1.929 | 3.523 | 709.57 | 100.00% | 0 |
