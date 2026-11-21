# Resumen de ejecución: `20261121T044019Z_bench_mongodb_e8e5d5`

- **Modo:** `benchmark`
- **Motor:** `mongodb` (document)
- **Dataset:** `synthetic_1000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:40:19Z`
- **Fin UTC:** `2026-11-21T04:40:28Z`
- **Conexión (ms):** `27.517` | **Esquema (ms):** `38.004` | **Carga (ms):** `23.900` | **Índices (ms):** `41.827`
- **Almacenamiento reportado (bytes):** `122880`
- **Pico memoria Docker (MiB):** `407.0` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `D1_read_taxon_dossier` | 30 | 0.604 | 0.900 | 1.072 | 1561.96 | 100.00% | 0 |
| `D2_nested_attribute_query` | 30 | 0.981 | 1.389 | 1.457 | 984.58 | 100.00% | 0 |
| `D3_versioned_dossier_update` | 30 | 2.135 | 2.634 | 2.747 | 453.22 | 100.00% | 0 |
| `D4_bulk_raw_source_insert` | 30 | 1.315 | 2.211 | 3.718 | 674.23 | 100.00% | 0 |
